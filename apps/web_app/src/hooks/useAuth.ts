import { useAuthStore, User } from '../store/auth';
import { apiClient } from '../lib/api';

export const useAuth = () => {
  const {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    error,
    setAuth,
    clearAuth,
    setLoading,
    setError,
  } = useAuthStore();

  const signIn = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.signIn(email, password);

      if (response.success && response.data) {
        const { user, access_token, refresh_token } = response.data;
        
        setAuth({
          user: user as User,
          accessToken: access_token,
          refreshToken: refresh_token,
        });
        
        return { success: true };
      } else {
        setError(response.error || 'Sign in failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Sign in failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.register(name, email, password);

      if (response.success && response.data) {
        const { user, access_token, refresh_token } = response.data;
        
        setAuth({
          user: user as User,
          accessToken: access_token,
          refreshToken: refresh_token,
        });
        
        return { success: true };
      } else {
        setError(response.error || 'Registration failed');
        return { success: false, error: response.error };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    clearAuth();
  };

  const validateTokenAsync = async () => {
    if (!accessToken) return false;

    try {
      const response = await apiClient.validateToken(accessToken);
      return response.success;
    } catch (error) {
      return false;
    }
  };

  const refreshTokenAsync = async () => {
    if (!refreshToken) return false;

    try {
      const response = await apiClient.refreshToken(refreshToken);
      
      if (response.success && response.data) {
        const { access_token, refresh_token } = response.data;
        
        setAuth({
          user: user!,
          accessToken: access_token,
          refreshToken: refresh_token,
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      return false;
    }
  };

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    error,
    
    // Actions
    signIn,
    register,
    signOut,
    validateTokenAsync,
    refreshTokenAsync,
    setError,
  };
};