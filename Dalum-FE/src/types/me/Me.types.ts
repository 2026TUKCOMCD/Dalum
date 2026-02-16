export type HistoryType = "search" | "styling";

export type HistoryItem = {
  id: string;
  type: HistoryType;
  createdAt: string; // "2026.01.15.(목) 05:28" or ISO
  thumbnailUrl?: string; // 있으면 이미지로
};
