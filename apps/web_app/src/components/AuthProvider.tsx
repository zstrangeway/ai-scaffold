'use client';

import { useEffect, ReactNode } from 'react';
import '../i18n';

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  useEffect(() => {
    // i18n is initialized when the module is imported
    // This effect ensures the component re-renders after i18n is ready
  }, []);

  return <>{children}</>;
}