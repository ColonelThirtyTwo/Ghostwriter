/// Tag editor.

import * as Y from "yjs";
import Tagify from "@yaireo/tagify";

import "../forms/styles.scss";
import { useEffect, useRef } from "react";

export function TagEditor(props: {
    connected: boolean;
    doc: Y.Doc;
    docKey: string;
    id?: string;
    className?: string;
}) {
    const inputRef = useRef<HTMLInputElement>(null);
    const taggify = useRef<Tagify | null>(null);
    useEffect(() => {
        taggify.current = new Tagify(inputRef.current!, {
            createInvalidTags: false,
            skipInvalid: true,
            classNames: {
                namespace: "tagify form-control",
            },
        });

        const map = props.doc.get(props.docKey, Y.Map);
        taggify.current.addTags(Array.from(map.keys()));

        map.observe((ev, _tx) => {
            for (const key of ev.keysChanged) {
                if (map.has(key) && !taggify.current?.isTagDuplicate(key))
                    taggify.current?.addTags([key]);
                else if (!map.has(key) && taggify.current?.isTagDuplicate(key))
                    taggify.current?.removeTags([key], true);
            }
        });

        // TODO: implement. no docs on these...
        taggify.current.on("add", (ev) => {
            console.log("add", ev.detail);
            map.set(ev.detail.data!.value, true);
        });
        taggify.current.on("remove", (ev) => {
            console.log("remove", ev.detail);
            map.delete(ev.detail.data!.value);
        });
        taggify.current.on("edit:updated", (ev) => {
            console.log("edit:updated", ev.detail);
        });

        return () => {
            taggify.current?.destroy();
        };
    }, []);

    return <input id={props.id} type="text" ref={inputRef} />;
}
