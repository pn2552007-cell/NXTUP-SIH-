import React from 'react';
import { Outlet } from 'react-router-dom';
import { AdminSidebar } from '../components/admin/AdminSidebar';
import { AdminTopBar } from '../components/admin/AdminTopBar';

export const AdminLayout = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-white">
      <AdminSidebar />
      <div className="flex flex-col flex-1 overflow-y-auto">
        <AdminTopBar />
        <main className="flex-1 p-6 overflow-auto bg-slate-900/30">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
