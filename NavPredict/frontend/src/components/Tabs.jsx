import React from 'react';

export const Tabs = ({ value, onValueChange, children, className = '' }) => (
  <div className={className}>{children}</div>
);

export const TabsList = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export const TabsTrigger = ({ value, children, onClick }) => (
  <button
    onClick={() => onClick?.(value)}
    className="px-4 py-2 rounded text-white font-poppins hover:bg-neon-blue/20 transition-colors"
  >
    {children}
  </button>
);

export const TabsContent = ({ value, children, ...props }) => (
  <div {...props}>{children}</div>
);
