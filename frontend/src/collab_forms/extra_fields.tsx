import { useMemo } from "react";
import {
    CheckboxInput,
    IntegerInput,
    NumberInput,
    PlainTextInput,
} from "./plain_editors";
import JsonEditor from "./json_editor";
import RichTextEditor from "./editor";
import Connection from "./connection";
import { XmlFragment } from "yjs";

/// Emitted from ExtraFieldsSpecSerializer
type ExtraFieldSpec = {
    internal_name: string;
    display_name: string;
    description: string;
    type:
        | "checkbox"
        | "single_line_text"
        | "rich_text"
        | "integer"
        | "float"
        | "json";
};

function useExtraFieldSpecs(): ExtraFieldSpec[] {
    return useMemo(
        () =>
            JSON.parse(
                document.getElementById("yjs-extra-field-specs")!.innerHTML
            ),
        []
    );
}

export default function ExtraFieldsSection(props: {
    connected: boolean;
    connection: Connection;
}) {
    const specs = useExtraFieldSpecs();

    return (
        <>
            {specs.map((spec) => (
                <div className="form-group col-md-12" key={spec.internal_name}>
                    <label>{spec.display_name}</label>
                    <ExtraFieldInput {...props} spec={spec} />
                    {spec.description && (
                        <small className="form-text text-muted">
                            {spec.description}
                        </small>
                    )}
                </div>
            ))}
        </>
    );
}

function ExtraFieldInput(props: {
    connected: boolean;
    connection: Connection;
    spec: ExtraFieldSpec;
}) {
    const map = props.connection.doc.getMap("extra_fields");
    switch (props.spec.type) {
        case "checkbox":
            return (
                <CheckboxInput
                    connected={props.connected}
                    map={map}
                    mapKey={props.spec.internal_name}
                    inputProps={{ className: "form-control mb-3" }}
                />
            );
        case "float":
            return (
                <NumberInput
                    connected={props.connected}
                    map={map}
                    mapKey={props.spec.internal_name}
                    inputProps={{ className: "form-control mb-3" }}
                />
            );
        case "integer":
            return (
                <IntegerInput
                    connected={props.connected}
                    map={map}
                    mapKey={props.spec.internal_name}
                    inputProps={{ className: "form-control mb-3" }}
                />
            );
        case "single_line_text":
            return (
                <PlainTextInput
                    connected={props.connected}
                    map={map}
                    mapKey={props.spec.internal_name}
                    inputProps={{ className: "form-control mb-3" }}
                />
            );
        case "rich_text":
            let frag = map.get(props.spec.internal_name);
            if (!(frag instanceof XmlFragment)) {
                if (!props.connected) return <p>Loading...</p>;
                frag = new XmlFragment();
                map.set(props.spec.internal_name, frag);
            }

            return (
                <RichTextEditor
                    connected={props.connected}
                    conn={props.connection}
                    fragment={frag as XmlFragment}
                />
            );
        case "json":
            return (
                <JsonEditor
                    connected={props.connected}
                    map={map}
                    mapKey={props.spec.internal_name}
                />
            );
        default:
            props.spec.type satisfies never;
            console.warn(
                "Unrecognized extra field type (this is a bug):",
                props.spec.type
            );
            return <></>;
    }
}
