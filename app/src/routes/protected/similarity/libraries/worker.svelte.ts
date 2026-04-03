self.onmessage = async (e: MessageEvent) => {
  const { files, url }: { files: File[], url: string } = e.data;

  for (let i = 0; i < files.length; i++) {
    const file: File = files[i];
    const chunkSize = 50 * 1024 * 1024; // 50MB
    const totalChunk = Math.ceil(file.size / chunkSize);

    for (let start = 0; start < file.size; start += chunkSize) {

      const chunk: Blob = file.slice(start, start + chunkSize);
      const formData = new FormData();
      formData.append("files", chunk);

      const indexChunk = Math.floor(start / chunkSize);
      const params: Record<string, any> = {
        filename: file.name,
        isInitial: start == 0 ? true : false,
        totalChunk: totalChunk,
        indexChunk: indexChunk,
      };

      const _url = new URL(url);
      _url.search = new URLSearchParams(params).toString();
      const res = await fetch(_url, {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(10800000), // 3 hour
      });

      if (!res.ok) {
        self.postMessage({ error: true });
      }
    }
  }

  self.postMessage({ error: false });
};
