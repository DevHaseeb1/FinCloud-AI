import { getData, postData, putData, deleteData } from "@/services/api";
import type { AwsConnection, AwsSetupResponse, AwsTestCheck, AwsFetchHistory } from "@/types/apiTypes";

export async function setupConnection(): Promise<AwsSetupResponse> {
  return postData<AwsSetupResponse>("/aws/connections/setup", {});
}

export async function testConnection(payload: {
  connection_id?: number;
  role_arn?: string;
  external_id?: string;
  access_key_id?: string;
  secret_access_key?: string;
  region?: string;
  s3_cur_bucket?: string;
  s3_cur_prefix?: string;
}): Promise<{ connection_id: number; overall_status: string; checks: AwsTestCheck[] }> {
  return postData("/aws/connections/test", payload);
}

export async function createConnection(payload: {
  name: string;
  account_id?: string;
  role_arn?: string;
  external_id?: string;
  access_key_id?: string;
  secret_access_key?: string;
  region?: string;
  s3_cur_bucket?: string;
  s3_cur_prefix?: string;
}): Promise<{ connection_id: number }> {
  return postData("/aws/connections", payload);
}

export async function listConnections(): Promise<{ connections: AwsConnection[] }> {
  return getData("/aws/connections");
}

export async function getConnection(id: number): Promise<{ connection: AwsConnection }> {
  return getData(`/aws/connections/${id}`);
}

export async function updateConnection(id: number, payload: Partial<AwsConnection>): Promise<{ connection_id: number }> {
  return putData(`/aws/connections/${id}`, payload);
}

export async function deleteConnection(id: number): Promise<void> {
  return deleteData(`/aws/connections/${id}`);
}

export async function fetchBillingData(payload: {
  connection_id: number;
  start_date?: string;
  end_date?: string;
  use_cur?: boolean;
}): Promise<{ connection_id: number; source: string; rows_fetched: number; rows_ingested: number }> {
  return postData("/aws/fetch", payload);
}

export async function getFetchHistory(connectionId: number): Promise<{ history: AwsFetchHistory[] }> {
  return getData(`/aws/connections/${connectionId}/history`);
}
