import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Shield, Clock, BookOpen } from 'lucide-react';

export const MobileNav: React.FC = () => {
  return (
    <nav aria-label="Mobile navigation" className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-slate-950/95 backdrop-blur-md border-t border-slate-800/80 px-2 py-2">
      <div className="flex items-center justify-around max-w-md mx-auto">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `flex flex-col items-center justify-center gap-1 py-1 px-3 rounded-xl text-[10px] font-medium transition-all ${
              isActive
                ? 'text-teal-400 bg-teal-500/10 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          <Home className="w-4 h-4" />
          <span>Home</span>
        </NavLink>

        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center gap-1 py-1 px-3 rounded-xl text-[10px] font-medium transition-all ${
              isActive
                ? 'text-teal-400 bg-teal-500/10 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          <Shield className="w-4 h-4" />
          <span>Shield</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center gap-1 py-1 px-3 rounded-xl text-[10px] font-medium transition-all ${
              isActive
                ? 'text-teal-400 bg-teal-500/10 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          <Clock className="w-4 h-4" />
          <span>Activity</span>
        </NavLink>

        <NavLink
          to="/safety"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center gap-1 py-1 px-3 rounded-xl text-[10px] font-medium transition-all ${
              isActive
                ? 'text-teal-400 bg-teal-500/10 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`
          }
        >
          <BookOpen className="w-4 h-4" />
          <span>Safety</span>
        </NavLink>
      </div>
    </nav>
  );
};
