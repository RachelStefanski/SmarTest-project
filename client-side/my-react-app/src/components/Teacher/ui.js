import React from "react";

// כפתור
export function Button({ children, className = "", ...props }) {
  return (
    <button
      className={`px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

// שדה קלט
export function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full px-3 py-2 border rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300 ${className}`}
      {...props}
    />
  );
}

// תווית
export function Label({ children, className = "", ...props }) {
  return (
    <label className={`block text-sm font-medium text-gray-700 mb-1 ${className}`} {...props}>
      {children}
    </label>
  );
}

// רשימת בחירה
export function Select({ children, className = "", ...props }) {
  return (
    <select
      className={`w-full px-3 py-2 border rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300 ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}

// תיבת טקסט
export function Textarea({ className = "", ...props }) {
  return (
    <textarea
      className={`w-full px-3 py-2 border rounded-xl shadow-sm focus:outline-none focus:ring focus:border-blue-300 ${className}`}
      {...props}
    />
  );
}

// כרטיס (Card)
export function Card({ children, className = "", ...props }) {
  return (
    <div
      className={`bg-white p-4 rounded-2xl shadow-md border border-gray-200 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
