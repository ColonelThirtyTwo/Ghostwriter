// Does a bunch of loading+saving in parallel, to help figure out a good value for postgres' max connections.
//
// Will need to run this in the collab-server docker container, ex with `docker compose run`.

import { createApolloClient } from "../collab_server/client";
import HANDLERS from "../collab_server/handlers";

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

const handler = HANDLERS.get(modelType);
if(handler === undefined)
    throw new Error("Unrecognized model type");

const gqlClient = createApolloClient();

let stop = false;
process.on("SIGINT", () => {
    stop = true;
    console.log("Stopping...");
});

const worker = async () => {
    const doc = await handler.load(gqlClient, modelId);
    while(!stop) {
        await handler.save(gqlClient, modelId, doc);
    }
};

const workers = [];
console.log("Starting... Ctrl+C to stop")
for(let i=0; i<numWorkers; i++) {
    workers.push(worker());
}

await Promise.all(workers);
process.exit(0);
