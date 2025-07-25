import { type ModelHandler } from "../base_handler";
import FindingHandler from "./finding";
import ObservationHandler from "./observation";
import ReportHandler from "./report";
import ReportFindingLinkHandler from "./report_finding_link";
import ReportObservationLinkHandler from "./report_observation_link";

// Extend this with your model handlers. See how-to-collab.md.
const HANDLERS: Map<string, ModelHandler> = new Map([
    ["observation", ObservationHandler],
    ["report_observation_link", ReportObservationLinkHandler],
    ["finding", FindingHandler],
    ["report_finding_link", ReportFindingLinkHandler],
    ["report", ReportHandler],
]);
export default HANDLERS;
