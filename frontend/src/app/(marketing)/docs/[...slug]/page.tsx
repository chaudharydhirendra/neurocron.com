import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  Calendar,
  Edit,
  BookOpen,
} from "lucide-react";
import { getDocBySlug, getAllDocSlugs } from "@/lib/docs/content";

interface DocPageProps {
  params: Promise<{ slug: string[] }>;
}

export async function generateStaticParams() {
  const slugs = getAllDocSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: DocPageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const doc = getDocBySlug(resolvedParams.slug);

  if (!doc) {
    return { title: "Not Found" };
  }

  return {
    title: doc.title,
    description: doc.description,
    openGraph: {
      title: `${doc.title} | NeuroCron Docs`,
      description: doc.description,
    },
  };
}

// Simple markdown-like renderer
function renderContent(content: string) {
  const lines = content.trim().split("\n");
  const elements: React.ReactNode[] = [];
  let currentList: string[] = [];
  let inCodeBlock = false;
  let codeContent: string[] = [];
  let codeLanguage = "";
  let inTable = false;
  let tableHeaders: string[] = [];
  let tableRows: string[][] = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="list-disc pl-6 space-y-2 mb-6">
          {currentList.map((item, i) => (
            <li key={i} className="text-white/70">{item}</li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  const flushTable = () => {
    if (tableHeaders.length > 0) {
      elements.push(
        <div key={`table-${elements.length}`} className="overflow-x-auto mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                {tableHeaders.map((header, i) => (
                  <th key={i} className="px-4 py-3 text-left font-semibold text-white/80">
                    {header.trim()}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, i) => (
                <tr key={i} className="border-b border-white/5">
                  {row.map((cell, j) => (
                    <td key={j} className="px-4 py-3 text-white/60">
                      {cell.trim()}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableHeaders = [];
      tableRows = [];
      inTable = false;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks
    if (line.startsWith("```")) {
      if (inCodeBlock) {
        elements.push(
          <pre key={`code-${elements.length}`} className="bg-midnight-100 rounded-xl p-4 overflow-x-auto mb-6 border border-white/10">
            <code className="text-sm text-white/80 font-mono">{codeContent.join("\n")}</code>
          </pre>
        );
        codeContent = [];
        inCodeBlock = false;
      } else {
        flushList();
        flushTable();
        codeLanguage = line.slice(3);
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeContent.push(line);
      continue;
    }

    // Tables
    if (line.startsWith("|")) {
      if (!inTable) {
        flushList();
        inTable = true;
        const cells = line.split("|").filter(c => c.trim());
        tableHeaders = cells;
      } else if (line.includes("---")) {
        // Skip separator line
        continue;
      } else {
        const cells = line.split("|").filter(c => c.trim());
        tableRows.push(cells);
      }
      continue;
    } else if (inTable) {
      flushTable();
    }

    // Headers
    if (line.startsWith("# ")) {
      flushList();
      elements.push(
        <h1 key={`h1-${elements.length}`} className="text-4xl font-bold mb-6 mt-8 first:mt-0">
          {line.slice(2)}
        </h1>
      );
      continue;
    }
    if (line.startsWith("## ")) {
      flushList();
      elements.push(
        <h2 key={`h2-${elements.length}`} className="text-2xl font-bold mb-4 mt-10 scroll-mt-24" id={line.slice(3).toLowerCase().replace(/\s+/g, "-")}>
          {line.slice(3)}
        </h2>
      );
      continue;
    }
    if (line.startsWith("### ")) {
      flushList();
      elements.push(
        <h3 key={`h3-${elements.length}`} className="text-xl font-semibold mb-3 mt-8 scroll-mt-24" id={line.slice(4).toLowerCase().replace(/\s+/g, "-")}>
          {line.slice(4)}
        </h3>
      );
      continue;
    }
    if (line.startsWith("#### ")) {
      flushList();
      elements.push(
        <h4 key={`h4-${elements.length}`} className="text-lg font-semibold mb-2 mt-6">
          {line.slice(5)}
        </h4>
      );
      continue;
    }

    // Lists
    if (line.startsWith("- ") || line.startsWith("* ")) {
      currentList.push(line.slice(2));
      continue;
    }
    if (/^\d+\.\s/.test(line)) {
      currentList.push(line.replace(/^\d+\.\s/, ""));
      continue;
    }

    // Blockquotes
    if (line.startsWith("> ")) {
      flushList();
      elements.push(
        <blockquote key={`quote-${elements.length}`} className="border-l-4 border-electric pl-4 py-2 mb-6 text-white/70 italic">
          {line.slice(2)}
        </blockquote>
      );
      continue;
    }

    // Horizontal rule
    if (line.match(/^---+$/)) {
      flushList();
      elements.push(<hr key={`hr-${elements.length}`} className="border-white/10 my-8" />);
      continue;
    }

    // Paragraphs
    if (line.trim()) {
      flushList();
      // Process inline formatting
      let text = line
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/`(.+?)`/g, '<code class="bg-white/10 px-1.5 py-0.5 rounded text-electric text-sm">$1</code>')
        .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="text-electric hover:underline">$1</a>');

      elements.push(
        <p
          key={`p-${elements.length}`}
          className="text-white/70 leading-relaxed mb-4"
          dangerouslySetInnerHTML={{ __html: text }}
        />
      );
    }
  }

  flushList();
  flushTable();

  return elements;
}

export default async function DocPage({ params }: DocPageProps) {
  const resolvedParams = await params;
  const doc = getDocBySlug(resolvedParams.slug);

  if (!doc) {
    notFound();
  }

  return (
    <article className="pb-16">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-white/50 mb-8">
        <Link href="/docs" className="hover:text-white transition">
          Docs
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-white/70">{doc.category}</span>
        <ChevronRight className="w-4 h-4" />
        <span className="text-white">{doc.title}</span>
      </nav>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-white/50 mb-8">
        <span className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          {doc.readTime} read
        </span>
        <span className="flex items-center gap-1">
          <Calendar className="w-4 h-4" />
          Updated {doc.lastUpdated}
        </span>
      </div>

      {/* Content */}
      <div className="prose prose-invert max-w-none">
        {renderContent(doc.content)}
      </div>

      {/* Navigation */}
      <nav className="flex items-center justify-between mt-16 pt-8 border-t border-white/10">
        {doc.prevPage ? (
          <Link
            href={doc.prevPage.href}
            className="flex items-center gap-2 text-white/60 hover:text-electric transition group"
          >
            <ChevronLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
            <div>
              <div className="text-xs text-white/40">Previous</div>
              <div className="font-medium">{doc.prevPage.title}</div>
            </div>
          </Link>
        ) : (
          <div />
        )}
        {doc.nextPage && (
          <Link
            href={doc.nextPage.href}
            className="flex items-center gap-2 text-white/60 hover:text-electric transition group text-right"
          >
            <div>
              <div className="text-xs text-white/40">Next</div>
              <div className="font-medium">{doc.nextPage.title}</div>
            </div>
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        )}
      </nav>

      {/* Feedback */}
      <div className="mt-12 p-6 rounded-xl bg-white/5 border border-white/10">
        <h4 className="font-medium mb-2">Was this page helpful?</h4>
        <div className="flex items-center gap-4">
          <button className="px-4 py-2 rounded-lg bg-green-500/10 text-green-400 hover:bg-green-500/20 transition text-sm">
            Yes, it helped
          </button>
          <button className="px-4 py-2 rounded-lg bg-white/5 text-white/60 hover:bg-white/10 transition text-sm">
            Could be better
          </button>
        </div>
      </div>
    </article>
  );
}

