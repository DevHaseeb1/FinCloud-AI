import { postData } from "@/services/api";
import type { UploadResult } from "@/types/apiTypes";

export const uploadService = {
  uploadCsv: async (file: File, opts?: { mode?: string }) => {
    // #region agent log
    fetch('http://127.0.0.1:7588/ingest/0c48956d-7427-4dbd-a33f-a80373b53494',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'e15a98'},body:JSON.stringify({sessionId:'e15a98',runId:'pre-fix',hypothesisId:'H3',location:'frontend/src/services/uploadService.ts:uploadCsv',message:'Upload invoked',data:{name:file?.name,size:file?.size,type:file?.type,mode:opts?.mode,apiUrl:process.env.NEXT_PUBLIC_API_URL},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    const form = new FormData();
    form.append("file", file);
    if (opts?.mode) form.append("mode", opts.mode);
    return postData<UploadResult>("/upload/data", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

