import { gql } from "../../__generated__";
import { simpleModelHandler } from "../base_handler";
import * as Y from "yjs";
import { htmlToYjs, yjsToHtml } from "../yjs_converters";

const GET = gql(`
    query GET_PROJECT_NOTE($id: bigint!) {
        projectNote_by_pk(id: $id) {
            note
        }
    }
`);

const SET = gql(`
    mutation SET_PROJECT_NOTE($id: bigint!, $note: String!) {
        update_projectNote_by_pk(pk_columns:{id:$id}, _set:{note: $note}) {
            id
        }
    }
`);

const ProjectNoteHandler = simpleModelHandler(
    GET,
    SET,
    (doc, res) => {
        const obj = res.projectNote_by_pk;
        if (!obj) throw new Error("No object");
        htmlToYjs(obj.note, doc.get("note", Y.XmlFragment));
    },
    (doc, id) => {
        const note = yjsToHtml(doc.get("note", Y.XmlFragment));
        return {
            id,
            note,
        };
    }
);
export default ProjectNoteHandler;
