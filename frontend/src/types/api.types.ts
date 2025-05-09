export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface UserProfile {
    id: string;
    fullname: string;
    username: string;
    email: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface RegisterRequest {
    fullname: string;
    username: string;
    email: string;
    password: string;
}

export interface PasswordChangeRequest {
    current_password: string;
    new_password: string;
}

export interface ProfileUpdateRequest {
    fullname?: string;
    username?: string;
}

export interface APIResponse {
    message: string;
}