"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ImageIcon,
  Upload,
  FolderOpen,
  Tag,
  Grid3X3,
  List,
  Search,
  Filter,
  Plus,
  Loader2,
  Image,
  Video,
  FileText,
  Music,
  File,
  MoreHorizontal,
  Eye,
  Download,
  Trash2,
  Palette,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { authFetch } from "@/lib/auth";
import { cn } from "@/lib/utils";

interface Asset {
  id: string;
  name: string;
  description: string;
  asset_type: string;
  file_type: string;
  file_size: number;
  width: number;
  height: number;
  thumbnail_url: string;
  public_url: string;
  version: number;
  usage_count: number;
  created_at: string;
}

interface Folder {
  id: string;
  name: string;
  description: string;
  color: string;
  asset_count: number;
  subfolder_count: number;
}

export default function AssetsPage() {
  const { organization } = useAuth();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [activeTab, setActiveTab] = useState<"assets" | "folders" | "brand">("assets");
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string | null>(null);

  useEffect(() => {
    if (organization) {
      fetchData();
    }
  }, [organization]);

  const fetchData = async () => {
    if (!organization) return;
    setIsLoading(true);

    try {
      const [assetsRes, foldersRes] = await Promise.all([
        authFetch(`/api/v1/assets/assets?org_id=${organization.id}`),
        authFetch(`/api/v1/assets/folders?org_id=${organization.id}`),
      ]);

      if (assetsRes.ok) {
        const data = await assetsRes.json();
        setAssets(data.assets || []);
      }
      if (foldersRes.ok) {
        const data = await foldersRes.json();
        setFolders(data.folders || []);
      }
    } catch (error) {
      console.error("Failed to fetch assets:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getAssetIcon = (type: string) => {
    switch (type) {
      case "image":
      case "logo":
        return Image;
      case "video":
        return Video;
      case "document":
        return FileText;
      case "audio":
        return Music;
      default:
        return File;
    }
  };

  const assetTypes = [
    { id: null, label: "All", icon: Grid3X3 },
    { id: "image", label: "Images", icon: Image },
    { id: "video", label: "Videos", icon: Video },
    { id: "document", label: "Documents", icon: FileText },
    { id: "logo", label: "Logos", icon: Palette },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
              <ImageIcon className="w-5 h-5 text-white" />
            </div>
            BrandVault
          </h1>
          <p className="text-white/60 mt-1">
            Asset library with versioning and brand guidelines
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Upload className="w-4 h-4" />
          Upload Assets
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "assets", label: "Assets", icon: ImageIcon },
          { id: "folders", label: "Folders", icon: FolderOpen },
          { id: "brand", label: "Brand Guide", icon: Palette },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
              activeTab === tab.id
                ? "bg-electric text-white"
                : "text-white/60 hover:text-white hover:bg-white/5"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "assets" && (
        <>
          {/* Toolbar */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
              <input
                type="text"
                placeholder="Search assets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
            <div className="flex gap-2">
              {assetTypes.map((type) => (
                <button
                  key={type.id || "all"}
                  onClick={() => setSelectedType(type.id)}
                  className={cn(
                    "px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors",
                    selectedType === type.id
                      ? "bg-electric text-white"
                      : "bg-white/5 text-white/60 hover:text-white"
                  )}
                >
                  <type.icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{type.label}</span>
                </button>
              ))}
            </div>
            <div className="flex gap-1 bg-white/5 rounded-lg p-1">
              <button
                onClick={() => setViewMode("grid")}
                className={cn(
                  "p-2 rounded transition-colors",
                  viewMode === "grid" ? "bg-electric text-white" : "text-white/60"
                )}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={cn(
                  "p-2 rounded transition-colors",
                  viewMode === "list" ? "bg-electric text-white" : "text-white/60"
                )}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Assets Grid/List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-electric" />
            </div>
          ) : assets.length === 0 ? (
            <div className="card p-12 text-center">
              <ImageIcon className="w-16 h-16 mx-auto mb-4 text-white/20" />
              <h3 className="text-xl font-semibold mb-2">No assets yet</h3>
              <p className="text-white/50 mb-6">Upload your first asset to get started</p>
              <button className="btn-primary">
                <Upload className="w-4 h-4 mr-2" />
                Upload Asset
              </button>
            </div>
          ) : viewMode === "grid" ? (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {assets.map((asset, index) => {
                const Icon = getAssetIcon(asset.asset_type);
                return (
                  <motion.div
                    key={asset.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.02 }}
                    className="card overflow-hidden group cursor-pointer"
                  >
                    <div className="aspect-square bg-white/5 flex items-center justify-center relative">
                      {asset.thumbnail_url ? (
                        <img
                          src={asset.thumbnail_url}
                          alt={asset.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <Icon className="w-12 h-12 text-white/20" />
                      )}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button className="p-2 bg-white/20 rounded-lg hover:bg-white/30">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-2 bg-white/20 rounded-lg hover:bg-white/30">
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="p-3">
                      <div className="font-medium text-sm truncate">{asset.name}</div>
                      <div className="text-xs text-white/50 mt-1 flex items-center justify-between">
                        <span>{formatFileSize(asset.file_size)}</span>
                        <span>v{asset.version}</span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="card divide-y divide-white/5">
              {assets.map((asset) => {
                const Icon = getAssetIcon(asset.asset_type);
                return (
                  <div key={asset.id} className="p-4 flex items-center gap-4 hover:bg-white/5">
                    <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-white/40" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{asset.name}</div>
                      <div className="text-sm text-white/50">
                        {asset.asset_type} • {formatFileSize(asset.file_size)}
                        {asset.width && asset.height && ` • ${asset.width}×${asset.height}`}
                      </div>
                    </div>
                    <div className="text-sm text-white/50">
                      v{asset.version}
                    </div>
                    <div className="text-sm text-white/50">
                      {asset.usage_count} uses
                    </div>
                    <button className="p-2 hover:bg-white/10 rounded-lg">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {activeTab === "folders" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button className="btn-secondary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Folder
            </button>
          </div>
          {folders.length === 0 ? (
            <div className="card p-12 text-center">
              <FolderOpen className="w-16 h-16 mx-auto mb-4 text-white/20" />
              <h3 className="text-xl font-semibold mb-2">No folders yet</h3>
              <p className="text-white/50 mb-6">Create folders to organize your assets</p>
              <button className="btn-primary">Create Folder</button>
            </div>
          ) : (
            <div className="grid md:grid-cols-4 gap-4">
              {folders.map((folder) => (
                <div
                  key={folder.id}
                  className="card p-4 cursor-pointer hover:border-electric/50 transition-colors"
                >
                  <FolderOpen
                    className="w-12 h-12 mb-3"
                    style={{ color: folder.color || "#0066FF" }}
                  />
                  <div className="font-medium">{folder.name}</div>
                  <div className="text-sm text-white/50 mt-1">
                    {folder.asset_count} assets • {folder.subfolder_count} folders
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === "brand" && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Brand Colors</h3>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-white/60 mb-2">Primary Colors</div>
                <div className="flex gap-2">
                  <div className="w-12 h-12 rounded-lg bg-electric" title="#0066FF" />
                  <div className="w-12 h-12 rounded-lg bg-purple-500" title="#8B5CF6" />
                  <button className="w-12 h-12 rounded-lg border-2 border-dashed border-white/20 flex items-center justify-center text-white/40 hover:text-white hover:border-white/40">
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
              </div>
              <div>
                <div className="text-sm text-white/60 mb-2">Secondary Colors</div>
                <div className="flex gap-2">
                  <div className="w-12 h-12 rounded-lg bg-green-500" />
                  <div className="w-12 h-12 rounded-lg bg-yellow-500" />
                  <button className="w-12 h-12 rounded-lg border-2 border-dashed border-white/20 flex items-center justify-center text-white/40 hover:text-white hover:border-white/40">
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Typography</h3>
            <div className="space-y-4">
              <div>
                <div className="text-sm text-white/60 mb-2">Primary Font</div>
                <div className="text-2xl font-bold">Space Grotesk</div>
              </div>
              <div>
                <div className="text-sm text-white/60 mb-2">Secondary Font</div>
                <div className="text-xl">Inter</div>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Logos</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="aspect-square bg-white/5 rounded-lg flex items-center justify-center">
                <ImageIcon className="w-12 h-12 text-white/20" />
              </div>
              <div className="aspect-square bg-black rounded-lg flex items-center justify-center">
                <ImageIcon className="w-12 h-12 text-white/20" />
              </div>
            </div>
            <button className="btn-secondary w-full mt-4">Upload Logo</button>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold mb-4">Voice & Tone</h3>
            <div className="space-y-2 text-white/60">
              <p>• Professional yet approachable</p>
              <p>• Confident and innovative</p>
              <p>• Clear and concise</p>
              <p>• Forward-thinking</p>
            </div>
            <button className="btn-secondary w-full mt-4">Edit Guidelines</button>
          </div>
        </div>
      )}
    </div>
  );
}

