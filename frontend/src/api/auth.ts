import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export interface GoogleAuthResponse {
  access: string;    // JWT Access token
  refresh: string;   // JWT Refresh token
  user: {
    id: number;
    email: string;
    username: string;
    avatar?: string;
  };
}

export async function loginWithGoogle(accessToken: string): Promise<GoogleAuthResponse> {
  const response = await axios.post<GoogleAuthResponse>(`${API_BASE_URL}/auth/google/`, {
    access_token: accessToken,
  });
  return response.data;
}
