import type { ReactNode } from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import MobileNav from "@/components/layout/MobileNav";

interface Props {
  children: ReactNode;
}

/**
 * DashboardLayout — persistent shell for all dashboard routes.
 *
 * Structure:
 *  - Desktop: fixed Sidebar (260 px) on the left, scrollable main area on the right.
 *  - Mobile: full-width main area with a fixed bottom MobileNav (80 px).
 *
 * The `pb-20` on <main> ensures content is never hidden behind the mobile
 * bottom nav bar. On md+ breakpoints that padding is removed.
 */
export default function DashboardLayout({ children }: Props) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Desktop sidebar — hidden below md breakpoint */}
      <Sidebar />

      {/* Main content column */}
      <div className="flex flex-col flex-1 min-w-0">
        <TopNav />
        <main className="flex-1 overflow-auto pb-20 md:pb-0 px-0">
          {children}
        </main>
        {/* Mobile bottom navigation — visible below md breakpoint */}
        <MobileNav />
      </div>
    </div>
  );
}
