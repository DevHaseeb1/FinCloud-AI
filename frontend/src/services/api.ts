import axios, { AxiosError } from "axios";
import type { ApiEnvelope } from "@/types/apiTypes";

export class ApiClientError extends Error {
  status?: number;
  details?: unknown;
  constructor(message: string, opts?: { status?: number; details?: unknown }) {
    super(message);
    this.name = "ApiClientError";
    this.status = opts?.status;
    this.details = opts?.details;
  }
}

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30_000,
});

export async function getData<T>(
  path: string,
  opts?: { params?: Record<string, unknown>; headers?: Record<string, string> },
) {
  try {
    // #region agent log
    fetch('http://127.0.0.1:7588/ingest/0c48956d-7427-4dbd-a33f-a80373b53494',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e15a98'},body:JSON.stringify({sessionId:'e15a98',runId:'pre-fix',hypothesisId:'H1',location:'frontend/src/services/api.ts:getData',message:'GET request start',data:{baseURL:process.env.NEXT_PUBLIC_API_URL,path,hasParams:!!opts?.params},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    const res = await api.get<ApiEnvelope<T>>(path, {
      params: opts?.params,
      headers: opts?.headers,
    });
    if (res.data?.status !== "success") {
      throw new ApiClientError(res.data?.message || "Request failed", {
        status: res.status,
        details: res.data,
      });
    }
    return res.data.data;
  } catch (err) {
    // #region agent log
    fetch('http://127.0.0.1:7588/ingest/0c48956d-7427-4dbd-a33f-a80373b53494',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e15a98'},body:JSON.stringify({sessionId:'e15a98',runId:'pre-fix',hypothesisId:'H1',location:'frontend/src/services/api.ts:getData',message:'GET request error',data:{baseURL:process.env.NEXT_PUBLIC_API_URL,path,isAxios:axios.isAxiosError(err),axiosMessage:axios.isAxiosError(err)?(err.message):undefined,status:axios.isAxiosError(err)?(err.response?.status):undefined,hasResponse:axios.isAxiosError(err)?!!err.response:undefined},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    throw toApiError(err);
  }
}

export async function postData<T>(
  path: string,
  body: unknown,
  opts?: { headers?: Record<string, string> },
) {
  try {
    // #region agent log
    fetch('http://127.0.0.1:7588/ingest/0c48956d-7427-4dbd-a33f-a80373b53494',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e15a98'},body:JSON.stringify({sessionId:'e15a98',runId:'pre-fix',hypothesisId:'H2',location:'frontend/src/services/api.ts:postData',message:'POST request start',data:{baseURL:process.env.NEXT_PUBLIC_API_URL,path,bodyType:body instanceof FormData?'FormData':typeof body,hasCustomHeaders:!!opts?.headers},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    const res = await api.post<ApiEnvelope<T>>(path, body, {
      headers: opts?.headers,
    });
    if (res.data?.status !== "success") {
      throw new ApiClientError(res.data?.message || "Request failed", {
        status: res.status,
        details: res.data,
      });
    }
    return res.data.data;
  } catch (err) {
    // #region agent log
    fetch('http://127.0.0.1:7588/ingest/0c48956d-7427-4dbd-a33f-a80373b53494',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e15a98'},body:JSON.stringify({sessionId:'e15a98',runId:'pre-fix',hypothesisId:'H2',location:'frontend/src/services/api.ts:postData',message:'POST request error',data:{baseURL:process.env.NEXT_PUBLIC_API_URL,path,isAxios:axios.isAxiosError(err),axiosMessage:axios.isAxiosError(err)?(err.message):undefined,status:axios.isAxiosError(err)?(err.response?.status):undefined,hasResponse:axios.isAxiosError(err)?!!err.response:undefined,errorCode:axios.isAxiosError(err)?((err as any).code):undefined},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    throw toApiError(err);
  }
}

function toApiError(err: unknown) {
  if (err instanceof ApiClientError) return err;
  if (axios.isAxiosError(err)) {
    const ax = err as AxiosError<any>;
    const message =
      ax.response?.data?.message ||
      ax.message ||
      "Network error calling backend API";
    return new ApiClientError(message, {
      status: ax.response?.status,
      details: ax.response?.data,
    });
  }
  return new ApiClientError("Unexpected error calling backend API", {
    details: err,
  });
}

