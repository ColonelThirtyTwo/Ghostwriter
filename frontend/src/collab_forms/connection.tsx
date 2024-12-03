import { useEffect, useRef, useState } from "react";
import { WebsocketProvider } from "y-websocket";
import * as Y from "yjs";

export default class Connection {
    public doc: Y.Doc;
    public provider: WebsocketProvider;

    constructor(wspath: string, room: string, username: string) {
        this.doc = new Y.Doc();
        this.provider = new WebsocketProvider(wspath, room, this.doc);
        this.provider.awareness.setLocalStateField("user", {
            name: username,
            color: hsv_to_rgb((this.doc.clientID % 255) / 255.0, 0.5, 1.0),
        });
    }

    destroy() {
        this.provider.destroy();
        this.doc.destroy();
    }
}

export function usePageConnection(): {
    connection: Connection;
    status:
        | "disconnected"
        | "connecting"
        | "initialSyncing"
        | "syncing"
        | "idle";
    connected: boolean;
} {
    const [status, setStatus] = useState<
        "disconnected" | "connecting" | "connected"
    >("disconnected");
    const [synced, setSynced] = useState<boolean>(false);
    const [initialSyncDone, setInitialSyncDone] = useState<boolean>(false);

    // Type as `Connection` because that's what it's gonna be outside of the initial setup
    const connection = useRef<Connection>(null as unknown as Connection);
    if (connection.current === null) {
        const url = document.getElementById("yjs-connection-url")!.innerHTML;
        const username = document.getElementById(
            "yjs-connection-username"
        )!.innerHTML;
        connection.current = new Connection(url, "", username);
        connection.current.provider.on(
            "status",
            ({ status }: { status: any }) => {
                setStatus(status);
                if (status === "disconnected" || status === "connecting")
                    setInitialSyncDone(false);
            }
        );
        connection.current.provider.on("sync", (synced: boolean) => {
            setSynced(synced);
            if (synced) {
                setInitialSyncDone(true);
            }
        });
    }
    useEffect(
        () => () => {
            connection.current?.destroy();
        },
        []
    );

    let outStatus;
    if (status === "connected") {
        if (!initialSyncDone) outStatus = "initialSyncing" as const;
        else if (synced) outStatus = "idle" as const;
        else outStatus = "syncing" as const;
    } else {
        outStatus = status;
    }

    return {
        connection: connection.current,
        status: outStatus,
        connected: outStatus === "idle" || outStatus === "syncing",
    };
}

function hsv_to_rgb(h: number, s: number, v: number) {
    const i = Math.floor(h * 6);
    const f = h * 6 - i;
    const p = v * (1 - s);
    const q = v * (1 - f * s);
    const t = v * (1 - (1 - f) * s);

    let r, g, b;
    switch (i % 6) {
        case 0:
            (r = v), (g = t), (b = p);
            break;
        case 1:
            (r = q), (g = v), (b = p);
            break;
        case 2:
            (r = p), (g = v), (b = t);
            break;
        case 3:
            (r = p), (g = q), (b = v);
            break;
        case 4:
            (r = t), (g = p), (b = v);
            break;
        case 5:
            (r = v), (g = p), (b = q);
            break;
    }

    const to_hex = (n: number) => {
        var str = Math.round(n * 255).toString(16);
        return str.length == 1 ? "0" + str : str;
    };

    return `#${to_hex(r!)}${to_hex(g!)}${to_hex(b!)}`;
}

const STATUS_LOOKUP = {
    disconnected: "Disconnected",
    connecting: "Connecting...",
    initialSyncing: "Synchronizing...",
    syncing: "Synchronizing...",
    idle: "Saved",
} as const;

export function ConnectionStatus(props: {
    status:
        | "disconnected"
        | "connecting"
        | "initialSyncing"
        | "syncing"
        | "idle";
}) {
    return (
        <div className="col-md-12">
            <small className="form-text text-muted">
                {STATUS_LOOKUP[props.status]}
            </small>
        </div>
    );
}
