export const isDev = true;

export let baseUrl: string;
export let apiUrl: string;
if (isDev) {
  baseUrl = "http://localhost:5173"; // npm run dev
  // apiUrl = "http://localhost:4175"; // FastAPI (home)
  // baseUrl = "http://10.168.1.188:4176";
  // apiUrl = "http://10.168.1.11:4178"; // FastAPI (office)
  apiUrl = "http://10.168.1.14:4178"; // FastAPI (office)
} else {
  baseUrl = "http://10.168.1.14:4176"; // npm run build
  // apiUrl = "http://localhost:4175"; // FastAPI
  // apiUrl = "http://10.168.1.11:4178"; // FastAPI
  apiUrl = "http://10.168.1.14:4178"; // FastAPI
}

export const nginxUrl = "http://10.168.1.14:4179";

export const cookiesAuth = "my-user";
// export const paginationLimit = 40;
