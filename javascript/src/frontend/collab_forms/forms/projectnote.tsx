import ReactModal from "react-modal";
import { ConnectionStatus, usePageConnection } from "../connection";
import RichTextEditor from "../rich_text_editor";
import { createRoot } from "react-dom/client";

function ProjectNoteForm() {
    const { provider, status, connected } = usePageConnection({
        model: "projectnote",
    });

    return (
        <>
            <ConnectionStatus status={status} />

            <div className="form-row">
                <div className="form-group col-md-12">
                    <label>Note</label>
                    <RichTextEditor
                        connected={connected}
                        provider={provider}
                        fragment={provider.document.getXmlFragment("note")}
                    />
                </div>
            </div>
        </>
    );
}

document.addEventListener("DOMContentLoaded", () => {
    ReactModal.setAppElement(
        document.querySelector("div.wrapper") as HTMLElement
    );
    const root = createRoot(document.getElementById("collab-form-container")!);
    root.render(<ProjectNoteForm />);
});
