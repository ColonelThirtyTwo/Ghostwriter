// Does a bunch of loading+saving in parallel, to help figure out a good value for postgres' max connections.
//
// Will need to run this in the collab-server docker container, ex with `docker compose run`.

import { Worker, isMainThread, parentPort, workerData } from "node:worker_threads";

import { createApolloClient } from "../collab_server/client";
import HANDLERS from "../collab_server/handlers";

type WorkerData = {
    index: number;
    handler: string;
    id: number;
    progress: SharedArrayBuffer,
};

if(isMainThread) {
    if(process.argv.length !== 5 || process.argv.includes("-h", 2) || process.argv.includes("--help", 2)) {
        console.error("Usage: stress_test (num_workers) (model_type) (model_id)")
        process.exit(2)
    }

    const numWorkers = parseInt(process.argv[2]);
    const modelType = process.argv[3];
    const modelId = parseInt(process.argv[4]);

    if(numWorkers !== numWorkers || modelId !== modelId) {
        throw new Error("Invalid argument");
    }

    if(!HANDLERS.has(modelType))
        throw new Error("Unrecognized model type");

    const workers: Worker[] = [];
    const workerPromises: Promise<undefined>[] = [];
    let stop = false;

    process.on("SIGINT", () => {
        if(stop) {
            process.exit(7)
        } else {
            stop = true;
            for(const worker of workers)
                worker.postMessage("stop");
            console.log("\nStopping...");
        }
    });

    const progress = new SharedArrayBuffer(numWorkers * Uint32Array.BYTES_PER_ELEMENT);

    console.log("Starting... Ctrl+C to stop")
    for(let i=0; i<numWorkers; i++) {
    const workerData: WorkerData = {
            index: i,
            handler: modelType,
            id: modelId,
            progress,
        };
        const worker = new Worker(import.meta.filename, {
            workerData,
        });
        workers.push(worker);
        workerPromises.push(new Promise((resolve, reject) => {
            worker.on("error", reject);
            worker.on("exit", code => {
                if(code !== 0)
                    reject(new Error(`Worker stopped with exit code ${code}`));
                else
                    resolve(undefined);
            });
        }));
    }

    workerPromises.push((async () => {
        const progressView = new Uint32Array(progress);
        while(!stop) {
            let str = "";
            for(let i=0; i<progressView.length; i++) {
                const n = Atomics.load(progressView, i);
                if(str !== "")
                    str += " ";
                str += String(n).padStart(4, " ")
            }
            process.stdout.write("\r");
            process.stdout.write(str);
            await new Promise((res) => setTimeout(res, 500));
        }
    })());

    await Promise.all(workerPromises);
    process.exit(0);
} else {
    let stop = false;
    parentPort!.on("close", () => {
        stop = true;
    });
    parentPort!.on("message", () => {
        stop = true;
    });

    const data = workerData as WorkerData;
    const progress = new Uint32Array(data.progress);
    const handler = HANDLERS.get(data.handler)!;

    const gqlClient = createApolloClient();

    const doc = await handler.load(gqlClient, data.id);
    while(!stop) {
        await handler.save(gqlClient, data.id, doc);
        Atomics.add(progress, data.index, 1)
    }
}
