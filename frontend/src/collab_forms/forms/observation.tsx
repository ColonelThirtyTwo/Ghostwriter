import { ConnectionStatus, usePageConnection } from "../connection";
import { PlainTextInput } from "../plain_editors";
import { TagEditor } from "../tag_editor";
import RichTextEditor from "../editor";
import { createRoot } from "react-dom/client";
import ExtraFieldsSection from "../extra_fields";

function ObservationForm() {
    const { connection, status, connected } = usePageConnection();

    return (
        <div className="form-row">
            <div className="form-group col-md-6 mb-0">
                <div className="form-group">
                    <label htmlFor="id_title">Title</label>
                    <div>
                        <PlainTextInput
                            inputProps={{
                                id: "id_title",
                                className: "form-control",
                            }}
                            connected={connected}
                            map={connection.doc.getMap("plain_fields")}
                            mapKey="title"
                        />
                    </div>
                </div>
            </div>
            <div className="form-group col-md-6 mb-0">
                <div className="form-group">
                    <label htmlFor="id_tags">Tags</label>
                    <div>
                        <TagEditor
                            id="id_tags"
                            className="form-control"
                            connected={connected}
                            doc={connection.doc}
                            docKey="tags"
                        />
                    </div>
                </div>
            </div>

            <div className="form-group col-md-12">
                <label>Description</label>
                <div>
                    <RichTextEditor
                        connected={connected}
                        conn={connection}
                        fragment={connection.doc.getXmlFragment("description")}
                    />
                </div>
            </div>

            <ExtraFieldsSection connected={connected} connection={connection} />

            <ConnectionStatus status={status} />
        </div>
    );
}

document.addEventListener("DOMContentLoaded", () => {
    const root = createRoot(
        document.getElementById("observation-form-container")!
    );
    root.render(<ObservationForm />);
});
