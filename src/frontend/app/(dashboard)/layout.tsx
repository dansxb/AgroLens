import type { ReactNode } from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import MobileNav from "@/components/layout/MobileNav";

interface Props {
  children: ReactNode;
}

export default function DashboardLayout({ children }: Props) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Desktop sidebar */}
      <Sidebar />

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0">
        <TopNav />
        <main className="flex-1 overflow-auto pb-16 md:pb-0">
          {children}
        </main>
        {/* Mobile bottom nav */}
        <MobileNav />
      </div>
    </div>
  );
}
