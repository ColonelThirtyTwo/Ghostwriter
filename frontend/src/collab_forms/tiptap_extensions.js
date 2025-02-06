// NOTE: This file is ALSO imported in collab-server!
// Collab extensions aren't included here since they require runtime configuration. They don't
// change the schema.
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import Link from "@tiptap/extension-link";
import TextAlign from "@tiptap/extension-text-align";
import Table from "@tiptap/extension-table";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import TableRow from "@tiptap/extension-table-row";
import PageBreak from "./tiptap_ext/pagebreak.ts";
const EXTENSIONS = [
    StarterKit.configure({
        history: false,
    }),
    Underline,
    Link,
    TextAlign.configure({
        types: ["heading", "paragraph"],
    }),
    Table,
    TableRow,
    TableHeader,
    TableCell,
    PageBreak,
];
export default EXTENSIONS;
