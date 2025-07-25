import * as apollo from "@apollo/client/core/index.js";
import { setContext } from "@apollo/client/link/context/index.js";
import { env } from "node:process";
import * as Y from "yjs";
import { yXmlFragmentToProseMirrorRootNode, prosemirrorToYXmlFragment } from "y-prosemirror";
import { createHTMLDocument, parseHTML } from "zeed-dom";
import { Slice, Fragment, DOMSerializer, DOMParser } from "@tiptap/pm/model";
import { Node, isNodeSelection, mergeAttributes, getSchema } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import TextAlign from "@tiptap/extension-text-align";
import Table from "@tiptap/extension-table";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import TableRow from "@tiptap/extension-table-row";
import Subscript from "@tiptap/extension-subscript";
import Superscript from "@tiptap/extension-superscript";
import { TextSelection, NodeSelection } from "@tiptap/pm/state";
import { jsxDEV } from "react/jsx-dev-runtime";
import { ReactNodeViewRenderer, NodeViewWrapper } from "@tiptap/react";
import React, { useContext } from "react";
import CodeBlock from "@tiptap/extension-code-block";
import Bold from "@tiptap/extension-bold";
import Italic from "@tiptap/extension-italic";
import Underline from "@tiptap/extension-underline";
import Highlight from "@tiptap/extension-highlight";
import { ReplaceAroundStep } from "@tiptap/pm/transform";
import Heading from "@tiptap/extension-heading";
const { ApolloClient, createHttpLink, InMemoryCache } = apollo;
function createApolloClient() {
  const httpLink = createHttpLink({
    uri: "http://graphql_engine:8080/v1/graphql"
  });
  const authLink = setContext((_, { headers }) => {
    return {
      headers: {
        ...headers,
        "x-hasura-admin-secret": env["HASURA_GRAPHQL_ADMIN_SECRET"]
      }
    };
  });
  return new ApolloClient({
    link: authLink.concat(httpLink),
    cache: new InMemoryCache(),
    defaultOptions: {
      query: {
        fetchPolicy: "no-cache",
        errorPolicy: "all"
      },
      watchQuery: {
        fetchPolicy: "no-cache",
        errorPolicy: "all"
      }
    }
  });
}
const Get_FindingDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_FINDING" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "finding_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "title" } }, { "kind": "Field", "name": { "kind": "Name", "value": "description" } }, { "kind": "Field", "name": { "kind": "Name", "value": "impact" } }, { "kind": "Field", "name": { "kind": "Name", "value": "mitigation" } }, { "kind": "Field", "name": { "kind": "Name", "value": "replication_steps" } }, { "kind": "Field", "name": { "kind": "Name", "value": "hostDetectionTechniques" } }, { "kind": "Field", "name": { "kind": "Name", "value": "networkDetectionTechniques" } }, { "kind": "Field", "name": { "kind": "Name", "value": "references" } }, { "kind": "Field", "name": { "kind": "Name", "value": "findingGuidance" } }, { "kind": "Field", "name": { "kind": "Name", "value": "cvssScore" } }, { "kind": "Field", "name": { "kind": "Name", "value": "cvssVector" } }, { "kind": "Field", "name": { "kind": "Name", "value": "severity" }, "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "findingTypeId" } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFields" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "tags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "finding", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFieldSpec" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "targetModel" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "_eq" }, "value": { "kind": "StringValue", "value": "reporting.Finding", "block": false } }] } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "internalName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "type" } }] } }] } }] };
const Set_FindingDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "mutation", "name": { "kind": "Name", "value": "SET_FINDING" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "set" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "finding_set_input" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } }, "type": { "kind": "NonNullType", "type": { "kind": "ListType", "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "update_finding_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "pk_columns" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }] } }, { "kind": "Argument", "name": { "kind": "Name", "value": "_set" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "set" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "setTags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "finding", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }, { "kind": "Argument", "name": { "kind": "Name", "value": "tags" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }] } }] };
const Get_ObservationDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_OBSERVATION" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "reporting_observation_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "title" } }, { "kind": "Field", "name": { "kind": "Name", "value": "description" } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFields" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "tags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "observation", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFieldSpec" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "targetModel" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "_eq" }, "value": { "kind": "StringValue", "value": "reporting.Observation", "block": false } }] } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "internalName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "type" } }] } }] } }] };
const Set_ObservationDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "mutation", "name": { "kind": "Name", "value": "SET_OBSERVATION" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "title" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "description" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } }, "type": { "kind": "NonNullType", "type": { "kind": "ListType", "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "jsonb" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "update_reporting_observation_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "pk_columns" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }] } }, { "kind": "Argument", "name": { "kind": "Name", "value": "_set" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "title" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "title" } } }, { "kind": "ObjectField", "name": { "kind": "Name", "value": "description" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "description" } } }, { "kind": "ObjectField", "name": { "kind": "Name", "value": "extraFields" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "setTags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "observation", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }, { "kind": "Argument", "name": { "kind": "Name", "value": "tags" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }] } }] };
const Get_ReportDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_REPORT" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "report_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "extraFields" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFieldSpec" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "targetModel" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "_eq" }, "value": { "kind": "StringValue", "value": "reporting.Report", "block": false } }] } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "internalName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "type" } }] } }] } }] };
const EviDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "mutation", "name": { "kind": "Name", "value": "evi" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "jsonb" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "update_report_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "pk_columns" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }] } }, { "kind": "Argument", "name": { "kind": "Name", "value": "_set" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "extraFields" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }] } }] };
const Get_Report_Finding_LinkDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_REPORT_FINDING_LINK" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "reportedFinding_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "title" } }, { "kind": "Field", "name": { "kind": "Name", "value": "description" } }, { "kind": "Field", "name": { "kind": "Name", "value": "impact" } }, { "kind": "Field", "name": { "kind": "Name", "value": "mitigation" } }, { "kind": "Field", "name": { "kind": "Name", "value": "replication_steps" } }, { "kind": "Field", "name": { "kind": "Name", "value": "hostDetectionTechniques" } }, { "kind": "Field", "name": { "kind": "Name", "value": "networkDetectionTechniques" } }, { "kind": "Field", "name": { "kind": "Name", "value": "references" } }, { "kind": "Field", "name": { "kind": "Name", "value": "findingGuidance" } }, { "kind": "Field", "name": { "kind": "Name", "value": "cvssScore" } }, { "kind": "Field", "name": { "kind": "Name", "value": "cvssVector" } }, { "kind": "Field", "name": { "kind": "Name", "value": "severity" }, "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "findingTypeId" } }, { "kind": "Field", "name": { "kind": "Name", "value": "affectedEntities" } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFields" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "tags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "report_finding_link", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFieldSpec" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "targetModel" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "_eq" }, "value": { "kind": "StringValue", "value": "reporting.Finding", "block": false } }] } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "internalName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "type" } }] } }] } }] };
const Set_Report_Finding_LinkDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "mutation", "name": { "kind": "Name", "value": "SET_REPORT_FINDING_LINK" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "set" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "reportedFinding_set_input" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } }, "type": { "kind": "NonNullType", "type": { "kind": "ListType", "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "update_reportedFinding_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "pk_columns" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }] } }, { "kind": "Argument", "name": { "kind": "Name", "value": "_set" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "set" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "setTags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "report_finding_link", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }, { "kind": "Argument", "name": { "kind": "Name", "value": "tags" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }] } }] };
const Get_Report_Observation_LinkDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_REPORT_OBSERVATION_LINK" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "reporting_reportobservationlink_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "title" } }, { "kind": "Field", "name": { "kind": "Name", "value": "description" } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFields" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "tags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "report_observation_link", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "extraFieldSpec" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "targetModel" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "_eq" }, "value": { "kind": "StringValue", "value": "reporting.Observation", "block": false } }] } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "internalName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "type" } }] } }] } }] };
const Set_Report_Observation_LinkDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "mutation", "name": { "kind": "Name", "value": "SET_REPORT_OBSERVATION_LINK" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "bigint" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "title" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "description" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } }, "type": { "kind": "NonNullType", "type": { "kind": "ListType", "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "String" } } } } } }, { "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "jsonb" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "update_reporting_reportobservationlink_by_pk" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "pk_columns" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }] } }, { "kind": "Argument", "name": { "kind": "Name", "value": "_set" }, "value": { "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "title" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "title" } } }, { "kind": "ObjectField", "name": { "kind": "Name", "value": "description" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "description" } } }, { "kind": "ObjectField", "name": { "kind": "Name", "value": "extraFields" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "extraFields" } } }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }] } }, { "kind": "Field", "name": { "kind": "Name", "value": "setTags" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "model" }, "value": { "kind": "StringValue", "value": "report_observation_link", "block": false } }, { "kind": "Argument", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "id" } } }, { "kind": "Argument", "name": { "kind": "Name", "value": "tags" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "tags" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "tags" } }] } }] } }] };
const Get_Finding_TypesDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_FINDING_TYPES" }, "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "findingType" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "order_by" }, "value": { "kind": "ListValue", "values": [{ "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "EnumValue", "value": "asc" } }] }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }, { "kind": "Field", "name": { "kind": "Name", "value": "findingType" } }] } }] } }] };
const Get_SeveritiesDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "GET_SEVERITIES" }, "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "findingSeverity" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "order_by" }, "value": { "kind": "ListValue", "values": [{ "kind": "ObjectValue", "fields": [{ "kind": "ObjectField", "name": { "kind": "Name", "value": "id" }, "value": { "kind": "EnumValue", "value": "asc" } }] }] } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }, { "kind": "Field", "name": { "kind": "Name", "value": "severity" } }] } }] } }] };
const Query_EvidenceDocument = { "kind": "Document", "definitions": [{ "kind": "OperationDefinition", "operation": "query", "name": { "kind": "Name", "value": "QUERY_EVIDENCE" }, "variableDefinitions": [{ "kind": "VariableDefinition", "variable": { "kind": "Variable", "name": { "kind": "Name", "value": "where" } }, "type": { "kind": "NonNullType", "type": { "kind": "NamedType", "name": { "kind": "Name", "value": "evidence_bool_exp" } } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "evidence" }, "arguments": [{ "kind": "Argument", "name": { "kind": "Name", "value": "where" }, "value": { "kind": "Variable", "name": { "kind": "Name", "value": "where" } } }], "selectionSet": { "kind": "SelectionSet", "selections": [{ "kind": "Field", "name": { "kind": "Name", "value": "id" } }, { "kind": "Field", "name": { "kind": "Name", "value": "caption" } }, { "kind": "Field", "name": { "kind": "Name", "value": "description" } }, { "kind": "Field", "name": { "kind": "Name", "value": "friendlyName" } }, { "kind": "Field", "name": { "kind": "Name", "value": "document" } }] } }] } }] };
const documents = {
  '\n    query GET_FINDING($id: bigint!) {\n        finding_by_pk(id: $id) {\n            title,\n            description,\n            impact,\n            mitigation,\n            replication_steps,\n            hostDetectionTechniques,\n            networkDetectionTechniques,\n            references,\n            findingGuidance,\n            cvssScore,\n            cvssVector,\n            severity { id },\n            findingTypeId,\n            extraFields\n        }\n        tags(model: "finding", id: $id) {\n            tags\n        }\n        extraFieldSpec(where:{targetModel:{_eq:"reporting.Finding"}}) {\n            internalName, type\n        }\n    }\n': Get_FindingDocument,
  '\n    mutation SET_FINDING(\n        $id:bigint!,\n        $set:finding_set_input!,\n        $tags:[String!]!,\n    ) {\n        update_finding_by_pk(pk_columns:{id:$id}, _set:$set) {\n            id\n        }\n        setTags(model: "finding", id: $id, tags: $tags) {\n            tags\n        }\n    }\n': Set_FindingDocument,
  '\n    query GET_OBSERVATION($id: bigint!) {\n        reporting_observation_by_pk(id: $id) {\n            title, description, extraFields\n        }\n        tags(model: "observation", id: $id) {\n            tags\n        }\n        extraFieldSpec(where:{targetModel:{_eq:"reporting.Observation"}}) {\n            internalName, type\n        }\n    }\n': Get_ObservationDocument,
  '\n    mutation SET_OBSERVATION(\n        $id:bigint!,\n        $title:String!,\n        $description:String!,\n        $tags:[String!]!,\n        $extraFields:jsonb!,\n    ) {\n        update_reporting_observation_by_pk(pk_columns:{id:$id}, _set:{\n            title: $title,\n            description: $description,\n            extraFields: $extraFields,\n        }) {\n            id\n        }\n        setTags(model: "observation", id: $id, tags: $tags) {\n            tags\n        }\n    }\n': Set_ObservationDocument,
  '\n    query GET_REPORT($id: bigint!) {\n        report_by_pk(id: $id) {\n            extraFields\n        }\n        extraFieldSpec(where:{targetModel:{_eq:"reporting.Report"}}){\n            internalName, type\n        }\n    }\n': Get_ReportDocument,
  "\n    mutation evi($id: bigint!, $extraFields:jsonb!) {\n        update_report_by_pk(pk_columns:{id:$id}, _set:{extraFields: $extraFields}) {\n            id\n        }\n    }\n": EviDocument,
  '\n    query GET_REPORT_FINDING_LINK($id: bigint!) {\n        reportedFinding_by_pk(id: $id) {\n            title,\n            description,\n            impact,\n            mitigation,\n            replication_steps,\n            hostDetectionTechniques,\n            networkDetectionTechniques,\n            references,\n            findingGuidance,\n            cvssScore,\n            cvssVector,\n            severity { id },\n            findingTypeId,\n            affectedEntities,\n            extraFields\n        }\n        tags(model: "report_finding_link", id: $id) {\n            tags\n        }\n        extraFieldSpec(where:{targetModel:{_eq:"reporting.Finding"}}) {\n            internalName, type\n        }\n    }\n': Get_Report_Finding_LinkDocument,
  '\n    mutation SET_REPORT_FINDING_LINK(\n        $id:bigint!,\n        $set:reportedFinding_set_input!,\n        $tags:[String!]!,\n    ) {\n        update_reportedFinding_by_pk(pk_columns:{id:$id}, _set:$set) {\n            id\n        }\n        setTags(model: "report_finding_link", id: $id, tags: $tags) {\n            tags\n        }\n    }\n': Set_Report_Finding_LinkDocument,
  '\n    query GET_REPORT_OBSERVATION_LINK($id: bigint!) {\n        reporting_reportobservationlink_by_pk(id: $id) {\n            title, description, extraFields\n        }\n        tags(model: "report_observation_link", id: $id) {\n            tags\n        }\n        extraFieldSpec(where:{targetModel:{_eq:"reporting.Observation"}}) {\n            internalName, type\n        }\n    }\n': Get_Report_Observation_LinkDocument,
  '\n    mutation SET_REPORT_OBSERVATION_LINK(\n        $id:bigint!,\n        $title:String!,\n        $description:String!,\n        $tags:[String!]!,\n        $extraFields:jsonb!,\n    ) {\n        update_reporting_reportobservationlink_by_pk(pk_columns:{id:$id}, _set:{\n            title: $title,\n            description: $description,\n            extraFields: $extraFields,\n        }) {\n            id\n        }\n        setTags(model: "report_observation_link", id: $id, tags: $tags) {\n            tags\n        }\n    }\n': Set_Report_Observation_LinkDocument,
  "\n    query GET_FINDING_TYPES {\n        findingType(order_by:[{id: asc}]) {\n            id, findingType\n        }\n    }\n": Get_Finding_TypesDocument,
  "\n    query GET_SEVERITIES {\n        findingSeverity(order_by:[{id: asc}]) {\n            id, severity\n        }\n    }\n": Get_SeveritiesDocument,
  "\n    query QUERY_EVIDENCE($where: evidence_bool_exp!) {\n        evidence(where:$where) {\n            id, caption, description, friendlyName, document\n        }\n    }\n": Query_EvidenceDocument
};
function gql(source) {
  return documents[source] ?? {};
}
function simpleModelHandler(getQuery, setQuery, fillFields, mkQueryVars) {
  return {
    load: async (client, id) => {
      const res = await client.query({
        query: getQuery,
        variables: {
          id
        }
      });
      if (res.error || res.errors) {
        throw res.error || res.errors;
      }
      const doc = new Y.Doc();
      doc.transact(() => {
        fillFields(doc, res.data);
      });
      return doc;
    },
    async save(client, id, doc) {
      let queryVars;
      doc.transact(() => {
        queryVars = mkQueryVars(doc, id);
      });
      const res = await client.mutate({
        mutation: setQuery,
        variables: queryVars
      });
      if (res.errors) {
        throw res.errors;
      }
    }
  };
}
const PageBreak = Node.create({
  name: "pageBreak",
  group: "block",
  parseHTML() {
    return [
      {
        tag: "div",
        getAttrs: (node) => node.classList.contains("page-break") && null
      }
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return [
      "div",
      mergeAttributes(
        { class: "page-break", contenteditable: false },
        HTMLAttributes
      ),
      ["div", { class: "page-break-line" }],
      ["div", { class: "page-break-text" }, "Page Break"],
      ["div", { class: "page-break-line" }]
    ];
  },
  renderText() {
    return "\n";
  },
  addCommands() {
    return {
      setPageBreak: () => ({ chain, state }) => {
        const { selection } = state;
        const { $from: $originFrom, $to: $originTo } = selection;
        const currentChain = chain();
        if ($originFrom.parentOffset === 0) {
          currentChain.insertContentAt(
            {
              from: Math.max($originFrom.pos - 1, 0),
              to: $originTo.pos
            },
            {
              type: this.name
            }
          );
        } else if (isNodeSelection(selection)) {
          currentChain.insertContentAt($originTo.pos, {
            type: this.name
          });
        } else {
          currentChain.insertContent({ type: this.name });
        }
        return currentChain.command(({ tr, dispatch }) => {
          if (dispatch) {
            const { $to } = tr.selection;
            const posAfter = $to.end();
            if ($to.nodeAfter) {
              if ($to.nodeAfter.isTextblock) {
                tr.setSelection(
                  TextSelection.create(
                    tr.doc,
                    $to.pos + 1
                  )
                );
              } else if ($to.nodeAfter.isBlock) {
                tr.setSelection(
                  NodeSelection.create(
                    tr.doc,
                    $to.pos
                  )
                );
              } else {
                tr.setSelection(
                  TextSelection.create(
                    tr.doc,
                    $to.pos
                  )
                );
              }
            } else {
              const node = $to.parent.type.contentMatch.defaultType?.create();
              if (node) {
                tr.insert(posAfter, node);
                tr.setSelection(
                  TextSelection.create(
                    tr.doc,
                    posAfter + 1
                  )
                );
              }
            }
            tr.scrollIntoView();
          }
          return true;
        }).run();
      }
    };
  }
});
const Evidence = Node.create({
  name: "evidence",
  group: "block",
  draggable: true,
  addAttributes() {
    return {
      id: {
        default: null,
        parseHTML: (el) => el.getAttribute("data-evidence-id"),
        renderHTML: (attrs) => ({
          "data-evidence-id": attrs.id
        })
      }
    };
  },
  parseHTML() {
    return [
      {
        tag: "div",
        getAttrs: (node) => node.classList.contains("richtext-evidence") && null
      }
    ];
  },
  renderText({ node }) {
    return node.attrs.name ? "Evidence " + node.attrs.name : "Evidence";
  },
  renderHTML({ HTMLAttributes }) {
    return [
      "div",
      mergeAttributes(
        {
          class: "richtext-evidence"
        },
        HTMLAttributes
      )
    ];
  },
  addNodeView() {
    return ReactNodeViewRenderer(EvidenceView);
  },
  addCommands() {
    return {
      setEvidence: (options) => ({ commands }) => commands.insertContent({
        type: this.name,
        attrs: options
      })
    };
  },
  addKeyboardShortcuts() {
    return {
      "Mod-Shift-d": () => this.editor.options.element.dispatchEvent(
        new CustomEvent("openevidencemodal")
      )
    };
  }
});
const EvidencesContext = React.createContext(null);
function EvidenceView(props) {
  const id = parseInt(props.node.attrs.id);
  const ghostwriterEvidences = useContext(EvidencesContext);
  const evidence = ghostwriterEvidences && ghostwriterEvidences.evidence.find((v) => v.id === id);
  if (!evidence) {
    return /* @__PURE__ */ jsxDEV(NodeViewWrapper, { className: "richtext-evidence", children: /* @__PURE__ */ jsxDEV("span", { className: "richtext-evidence-missing", children: "(Evidence Missing)" }, void 0, false, {
      fileName: "/app/src/tiptap_gw/evidence.tsx",
      lineNumber: 109,
      columnNumber: 17
    }, this) }, void 0, false, {
      fileName: "/app/src/tiptap_gw/evidence.tsx",
      lineNumber: 108,
      columnNumber: 13
    }, this);
  }
  let img = null;
  if (evidence.document.endsWith(".png") || evidence.document.endsWith(".jpg") || evidence.document.endsWith(".jpeg")) {
    img = /* @__PURE__ */ jsxDEV("img", { src: ghostwriterEvidences.mediaUrl + evidence["document"] }, void 0, false, {
      fileName: "/app/src/tiptap_gw/evidence.tsx",
      lineNumber: 123,
      columnNumber: 13
    }, this);
  }
  return /* @__PURE__ */ jsxDEV(NodeViewWrapper, { className: "richtext-evidence", children: [
    /* @__PURE__ */ jsxDEV("span", { className: "richtext-evidence-name", children: evidence.friendlyName }, void 0, false, {
      fileName: "/app/src/tiptap_gw/evidence.tsx",
      lineNumber: 129,
      columnNumber: 13
    }, this),
    img,
    /* @__PURE__ */ jsxDEV("span", { className: "richtext-evidence-caption", children: "Evidence: " + evidence.caption }, void 0, false, {
      fileName: "/app/src/tiptap_gw/evidence.tsx",
      lineNumber: 133,
      columnNumber: 13
    }, this)
  ] }, void 0, true, {
    fileName: "/app/src/tiptap_gw/evidence.tsx",
    lineNumber: 128,
    columnNumber: 9
  }, this);
}
const FormattedCodeblock = CodeBlock.extend({
  marks: "_",
  // CodeBlock emits a <pre> and <code> but only parses the <pre>, so with marks, tiptap will think
  // everything is wrapped in an inline code mark. Alter the parser to unwrap the code element.
  parseHTML() {
    return [
      {
        tag: "pre",
        preserveWhitespace: "full",
        contentElement: (el) => el.childNodes.length == 1 && el.childNodes[0].nodeName === "CODE" ? el.childNodes[0] : el
      }
    ];
  }
});
let mkElem;
{
  mkElem = (await import("zeed-dom")).h;
}
const mkElem$1 = mkElem;
function unwrapClass(node, cls) {
  const n = node;
  n.classList.remove(cls);
  if (n.classList.length === 0) {
    return n;
  }
  const wrapper = mkElem$1("div");
  wrapper.appendChild(node.cloneNode(true));
  return wrapper;
}
const BoldCompat = Bold.extend({
  parseHTML() {
    const arr = Array.from(Bold.config.parseHTML.call(this));
    arr.push({
      tag: "span",
      getAttrs: (node) => node.classList.contains("bold") && null,
      contentElement: (node) => unwrapClass(node, "bold")
    });
    return arr;
  }
});
const ItalicCompat = Italic.extend({
  parseHTML() {
    const arr = Array.from(Italic.config.parseHTML.call(this));
    arr.push({
      tag: "span",
      getAttrs: (node) => node.classList.contains("italic") && null,
      contentElement: (node) => unwrapClass(node, "italic")
    });
    return arr;
  }
});
const UnderlineCompat = Underline.extend({
  parseHTML() {
    const arr = Array.from(Underline.config.parseHTML.call(this));
    arr.push({
      tag: "span",
      getAttrs: (node) => node.classList.contains("underline") && null,
      contentElement: (node) => unwrapClass(node, "underline")
    });
    return arr;
  }
});
const HighlightCompat = Highlight.extend({
  parseHTML() {
    const arr = Array.from(Highlight.config.parseHTML.call(this));
    arr.push({
      tag: "span",
      getAttrs: (node) => node.classList.contains("highlight") && null,
      contentElement: (node) => unwrapClass(node, "highlight")
    });
    return arr;
  }
});
const TableWithCaption = Node.create({
  name: "tableWithCaption",
  group: "block",
  content: "table tableCaption",
  isolating: true,
  // Parse before regular table
  priority: 101,
  parseHTML() {
    return [
      {
        tag: "div",
        getAttrs: (node) => node.classList.contains("collab-table-wrapper") && null
      },
      {
        // Hacky way to convert a table with a caption element to this wrapped format.
        tag: "table",
        getAttrs: (node) => {
          if (node.getElementsByTagName("caption").length > 0) {
            return null;
          }
          return false;
        },
        contentElement: (node) => {
          node = node.cloneNode(true);
          const caption = node.getElementsByTagName(
            "caption"
          )[0];
          caption.remove();
          const container = mkElem$1("div");
          container.appendChild(node);
          const captionP = mkElem$1("p");
          captionP.classList.add("collab-table-caption");
          container.appendChild(captionP);
          const captionSpan = mkElem$1("span");
          captionSpan.classList.add("collab-table-caption-content");
          for (const node2 of Array.from(caption.childNodes)) {
            captionSpan.appendChild(node2);
          }
          captionP.appendChild(captionSpan);
          return container;
        }
      }
    ];
  },
  renderHTML() {
    return ["div", { class: "collab-table-wrapper" }, 0];
  },
  renderText() {
    return "";
  }
});
function findParent($pos, name) {
  for (let d = $pos.depth - 1; d > 0; d--)
    if ($pos.node(d).type.name === name)
      return $pos.node(0).resolve($pos.before(d + 1));
  return null;
}
const TableCaption = Node.create({
  name: "tableCaption",
  content: "inline*",
  // Parse before regular p
  priority: 1001,
  parseHTML() {
    return [
      {
        tag: "p",
        getAttrs: (node) => node.classList.contains("collab-table-caption") && null,
        contentElement: ".collab-table-caption-content"
      }
    ];
  },
  renderHTML() {
    return [
      "p",
      { class: "collab-table-caption" },
      [
        "span",
        {
          class: "collab-table-caption-prefix",
          contenteditable: "false"
        },
        "Table #:"
      ],
      ["span", { class: "collab-table-caption-content" }, 0]
    ];
  },
  addCommands() {
    return {
      addCaption: () => ({ state, dispatch }) => {
        let $pos = findParent(state.selection.$head, "table");
        if (!$pos) return false;
        if ($pos.depth >= 2 && $pos.node(-1).type.name === "tableWithCaption")
          return false;
        if (dispatch) {
          const tr = state.tr;
          const start = $pos.before();
          const end = $pos.after();
          const fragment = Fragment.from(
            state.schema.nodes["tableWithCaption"].create(
              null,
              Fragment.from(
                state.schema.nodes["tableCaption"].create(
                  null,
                  Fragment.from(
                    state.schema.text("Caption")
                  )
                )
              )
            )
          );
          tr.step(
            new ReplaceAroundStep(
              start,
              end,
              start,
              end,
              new Slice(fragment, 0, 0),
              1
            )
          );
          dispatch(tr);
        }
        return true;
      },
      removeCaption: () => ({ state, dispatch }) => {
        let $pos = findParent(
          state.selection.$head,
          "tableWithCaption"
        );
        if (!$pos) return false;
        if (dispatch) {
          const tr = state.tr;
          const start = $pos.before() + 1;
          const end = start + $pos.node().child(0).nodeSize;
          tr.step(
            new ReplaceAroundStep(
              $pos.before(),
              $pos.after(),
              start,
              end,
              new Slice(Fragment.empty, 0, 0),
              0
            )
          );
          dispatch(tr);
        }
        return true;
      }
    };
  }
});
const HeadingWithId = Heading.extend({
  name: "gwheading",
  addAttributes() {
    const attrs = Heading.config.addAttributes.call(this);
    attrs.bookmark = {
      default: void 0,
      parseHTML: (el) => el.getAttribute("data-bookmark") || el.getAttribute("id"),
      renderHTML: (attr) => ({ "data-bookmark": attr.bookmark })
    };
    return attrs;
  },
  addCommands() {
    const cmds = Heading.config.addCommands.call(this);
    cmds.setHeadingBookmark = (name) => ({ commands, can }) => {
      if (!can().deleteNode(this.name)) return false;
      return commands.updateAttributes(this.name, { bookmark: name });
    };
    return cmds;
  }
});
const EXTENSIONS$1 = [
  StarterKit.configure({
    heading: false,
    history: false,
    codeBlock: false,
    bold: false,
    italic: false,
    horizontalRule: false
  }),
  HeadingWithId,
  BoldCompat,
  ItalicCompat,
  UnderlineCompat,
  FormattedCodeblock.configure({
    HTMLAttributes: {
      spellcheck: "false"
    }
  }),
  Link.configure({
    openOnClick: false
  }),
  TextAlign.configure({
    types: ["heading", "paragraph"]
  }),
  HighlightCompat,
  Table,
  TableRow,
  TableHeader,
  TableCell,
  PageBreak,
  Subscript,
  Superscript,
  Evidence,
  TableWithCaption,
  TableCaption
];
const EXTENSIONS = EXTENSIONS$1;
const SCHEMA = getSchema(EXTENSIONS);
function htmlToYjs(html, frag) {
  const dom = parseHTML(html);
  const node = DOMParser.fromSchema(SCHEMA).parse(dom);
  prosemirrorToYXmlFragment(node, frag);
}
function yjsToHtml(frag) {
  const node = yXmlFragmentToProseMirrorRootNode(frag, SCHEMA);
  const doc = DOMSerializer.fromSchema(SCHEMA).serializeFragment(
    node.content,
    {
      document: createHTMLDocument()
    }
  );
  return doc.render();
}
function tagsToYjs(tags, map) {
  for (const tag of tags) {
    map.set(tag, true);
  }
}
function yjsToTags(map) {
  let tags = [];
  for (const [key, value] of map.entries()) {
    if (value) tags.push(key);
  }
  return tags;
}
function extraFieldsToYdoc(specs, doc, json) {
  const extra_fields = doc.get("extra_fields", Y.Map);
  for (const spec of specs) {
    if (spec.type === "rich_text") {
      const frag = new Y.XmlFragment();
      extra_fields.set(spec.internalName, frag);
      htmlToYjs((json[spec.internalName] ?? "").toString(), frag);
    } else if (spec.type === "checkbox" || spec.type === "single_line_text" || spec.type === "integer" || spec.type === "float" || spec.type === "json") {
      extra_fields.set(spec.internalName, json[spec.internalName]);
    } else {
      throw new Error("Unrecognized extra field type: " + spec.type);
    }
  }
}
function extraFieldsFromYdoc(doc) {
  const extra_fields = doc.get("extra_fields", Y.Map);
  const out = {};
  for (const [key, value] of extra_fields.entries()) {
    if (value instanceof Y.XmlFragment) {
      out[key] = yjsToHtml(value);
    } else {
      out[key] = value;
    }
  }
  return out;
}
const GET$4 = gql(`
    query GET_FINDING($id: bigint!) {
        finding_by_pk(id: $id) {
            title,
            description,
            impact,
            mitigation,
            replication_steps,
            hostDetectionTechniques,
            networkDetectionTechniques,
            references,
            findingGuidance,
            cvssScore,
            cvssVector,
            severity { id },
            findingTypeId,
            extraFields
        }
        tags(model: "finding", id: $id) {
            tags
        }
        extraFieldSpec(where:{targetModel:{_eq:"reporting.Finding"}}) {
            internalName, type
        }
    }
`);
const SET$4 = gql(`
    mutation SET_FINDING(
        $id:bigint!,
        $set:finding_set_input!,
        $tags:[String!]!,
    ) {
        update_finding_by_pk(pk_columns:{id:$id}, _set:$set) {
            id
        }
        setTags(model: "finding", id: $id, tags: $tags) {
            tags
        }
    }
`);
const FindingHandler = simpleModelHandler(
  GET$4,
  SET$4,
  (doc, res) => {
    const obj = res.finding_by_pk;
    if (!obj) throw new Error("No object");
    const plain_fields = doc.get("plain_fields", Y.Map);
    plain_fields.set("title", obj.title);
    if (obj.cvssScore !== null && obj.cvssScore !== void 0)
      plain_fields.set("cvssScore", obj.cvssScore);
    plain_fields.set("cvssVector", obj.cvssVector);
    plain_fields.set("findingTypeId", obj.findingTypeId);
    plain_fields.set("severityId", obj.severity.id);
    htmlToYjs(obj.description, doc.get("description", Y.XmlFragment));
    htmlToYjs(obj.impact, doc.get("impact", Y.XmlFragment));
    htmlToYjs(obj.mitigation, doc.get("mitigation", Y.XmlFragment));
    htmlToYjs(
      obj.replication_steps,
      doc.get("replicationSteps", Y.XmlFragment)
    );
    htmlToYjs(
      obj.hostDetectionTechniques,
      doc.get("hostDetectionTechniques", Y.XmlFragment)
    );
    htmlToYjs(
      obj.networkDetectionTechniques,
      doc.get("networkDetectionTechniques", Y.XmlFragment)
    );
    htmlToYjs(obj.references, doc.get("references", Y.XmlFragment));
    htmlToYjs(
      obj.findingGuidance,
      doc.get("findingGuidance", Y.XmlFragment)
    );
    tagsToYjs(res.tags.tags, doc.get("tags", Y.Map));
    extraFieldsToYdoc(res.extraFieldSpec, doc, obj.extraFields);
  },
  (doc, id) => {
    const plainFields = doc.get("plain_fields", Y.Map);
    const extraFields = extraFieldsFromYdoc(doc);
    return {
      id,
      set: {
        title: plainFields.get("title") ?? "",
        cvssScore: plainFields.get("cvssScore") ?? null,
        cvssVector: plainFields.get("cvssVector") ?? "",
        findingTypeId: plainFields.get("findingTypeId"),
        severityId: plainFields.get("severityId"),
        description: yjsToHtml(doc.get("description", Y.XmlFragment)),
        impact: yjsToHtml(doc.get("impact", Y.XmlFragment)),
        mitigation: yjsToHtml(doc.get("mitigation", Y.XmlFragment)),
        replication_steps: yjsToHtml(
          doc.get("replicationSteps", Y.XmlFragment)
        ),
        hostDetectionTechniques: yjsToHtml(
          doc.get("hostDetectionTechniques", Y.XmlFragment)
        ),
        networkDetectionTechniques: yjsToHtml(
          doc.get("networkDetectionTechniques", Y.XmlFragment)
        ),
        references: yjsToHtml(doc.get("references", Y.XmlFragment)),
        findingGuidance: yjsToHtml(
          doc.get("findingGuidance", Y.XmlFragment)
        )
      },
      tags: yjsToTags(doc.get("tags", Y.Map)),
      extraFields
    };
  }
);
const GET$3 = gql(`
    query GET_OBSERVATION($id: bigint!) {
        reporting_observation_by_pk(id: $id) {
            title, description, extraFields
        }
        tags(model: "observation", id: $id) {
            tags
        }
        extraFieldSpec(where:{targetModel:{_eq:"reporting.Observation"}}) {
            internalName, type
        }
    }
`);
const SET$3 = gql(`
    mutation SET_OBSERVATION(
        $id:bigint!,
        $title:String!,
        $description:String!,
        $tags:[String!]!,
        $extraFields:jsonb!,
    ) {
        update_reporting_observation_by_pk(pk_columns:{id:$id}, _set:{
            title: $title,
            description: $description,
            extraFields: $extraFields,
        }) {
            id
        }
        setTags(model: "observation", id: $id, tags: $tags) {
            tags
        }
    }
`);
const ObservationHandler = simpleModelHandler(
  GET$3,
  SET$3,
  (doc, res) => {
    const obj = res.reporting_observation_by_pk;
    if (!obj) throw new Error("No object");
    const plain_fields = doc.get("plain_fields", Y.Map);
    plain_fields.set("title", obj.title);
    htmlToYjs(obj.description, doc.get("description", Y.XmlFragment));
    tagsToYjs(res.tags.tags, doc.get("tags", Y.Map));
    extraFieldsToYdoc(res.extraFieldSpec, doc, obj.extraFields);
  },
  (doc, id) => {
    const plainFields = doc.get("plain_fields", Y.Map);
    const extraFields = extraFieldsFromYdoc(doc);
    return {
      id,
      title: plainFields.get("title") ?? "",
      description: yjsToHtml(doc.get("description", Y.XmlFragment)),
      tags: yjsToTags(doc.get("tags", Y.Map)),
      extraFields
    };
  }
);
const GET$2 = gql(`
    query GET_REPORT($id: bigint!) {
        report_by_pk(id: $id) {
            extraFields
        }
        extraFieldSpec(where:{targetModel:{_eq:"reporting.Report"}}){
            internalName, type
        }
    }
`);
const SET$2 = gql(`
    mutation evi($id: bigint!, $extraFields:jsonb!) {
        update_report_by_pk(pk_columns:{id:$id}, _set:{extraFields: $extraFields}) {
            id
        }
    }
`);
const ReportHandler = simpleModelHandler(
  GET$2,
  SET$2,
  (doc, res) => {
    const obj = res.report_by_pk;
    if (!obj) throw new Error("No object");
    extraFieldsToYdoc(res.extraFieldSpec, doc, obj.extraFields);
  },
  (doc, id) => {
    const extraFields = extraFieldsFromYdoc(doc);
    return {
      id,
      extraFields
    };
  }
);
const GET$1 = gql(`
    query GET_REPORT_FINDING_LINK($id: bigint!) {
        reportedFinding_by_pk(id: $id) {
            title,
            description,
            impact,
            mitigation,
            replication_steps,
            hostDetectionTechniques,
            networkDetectionTechniques,
            references,
            findingGuidance,
            cvssScore,
            cvssVector,
            severity { id },
            findingTypeId,
            affectedEntities,
            extraFields
        }
        tags(model: "report_finding_link", id: $id) {
            tags
        }
        extraFieldSpec(where:{targetModel:{_eq:"reporting.Finding"}}) {
            internalName, type
        }
    }
`);
const SET$1 = gql(`
    mutation SET_REPORT_FINDING_LINK(
        $id:bigint!,
        $set:reportedFinding_set_input!,
        $tags:[String!]!,
    ) {
        update_reportedFinding_by_pk(pk_columns:{id:$id}, _set:$set) {
            id
        }
        setTags(model: "report_finding_link", id: $id, tags: $tags) {
            tags
        }
    }
`);
const ReportFindingLinkHandler = simpleModelHandler(
  GET$1,
  SET$1,
  (doc, res) => {
    const obj = res.reportedFinding_by_pk;
    if (!obj) throw new Error("No object");
    const plain_fields = doc.get("plain_fields", Y.Map);
    plain_fields.set("title", obj.title);
    if (obj.cvssScore !== null && obj.cvssScore !== void 0)
      plain_fields.set("cvssScore", obj.cvssScore);
    plain_fields.set("cvssVector", obj.cvssVector);
    plain_fields.set("findingTypeId", obj.findingTypeId);
    plain_fields.set("severityId", obj.severity.id);
    htmlToYjs(obj.description, doc.get("description", Y.XmlFragment));
    htmlToYjs(obj.impact, doc.get("impact", Y.XmlFragment));
    htmlToYjs(obj.mitigation, doc.get("mitigation", Y.XmlFragment));
    htmlToYjs(
      obj.replication_steps,
      doc.get("replicationSteps", Y.XmlFragment)
    );
    htmlToYjs(
      obj.hostDetectionTechniques,
      doc.get("hostDetectionTechniques", Y.XmlFragment)
    );
    htmlToYjs(
      obj.networkDetectionTechniques,
      doc.get("networkDetectionTechniques", Y.XmlFragment)
    );
    htmlToYjs(obj.references, doc.get("references", Y.XmlFragment));
    htmlToYjs(
      obj.findingGuidance,
      doc.get("findingGuidance", Y.XmlFragment)
    );
    htmlToYjs(
      obj.affectedEntities,
      doc.get("affectedEntities", Y.XmlFragment)
    );
    tagsToYjs(res.tags.tags, doc.get("tags", Y.Map));
    extraFieldsToYdoc(res.extraFieldSpec, doc, obj.extraFields);
  },
  (doc, id) => {
    const plainFields = doc.get("plain_fields", Y.Map);
    const extraFields = extraFieldsFromYdoc(doc);
    return {
      id,
      set: {
        title: plainFields.get("title") ?? "",
        cvssScore: plainFields.get("cvssScore") ?? null,
        cvssVector: plainFields.get("cvssVector") ?? "",
        findingTypeId: plainFields.get("findingTypeId"),
        severityId: plainFields.get("severityId"),
        description: yjsToHtml(doc.get("description", Y.XmlFragment)),
        impact: yjsToHtml(doc.get("impact", Y.XmlFragment)),
        mitigation: yjsToHtml(doc.get("mitigation", Y.XmlFragment)),
        replication_steps: yjsToHtml(
          doc.get("replicationSteps", Y.XmlFragment)
        ),
        hostDetectionTechniques: yjsToHtml(
          doc.get("hostDetectionTechniques", Y.XmlFragment)
        ),
        networkDetectionTechniques: yjsToHtml(
          doc.get("networkDetectionTechniques", Y.XmlFragment)
        ),
        references: yjsToHtml(doc.get("references", Y.XmlFragment)),
        findingGuidance: yjsToHtml(
          doc.get("findingGuidance", Y.XmlFragment)
        ),
        affectedEntities: yjsToHtml(
          doc.get("affectedEntities", Y.XmlFragment)
        )
      },
      tags: yjsToTags(doc.get("tags", Y.Map)),
      extraFields
    };
  }
);
const GET = gql(`
    query GET_REPORT_OBSERVATION_LINK($id: bigint!) {
        reporting_reportobservationlink_by_pk(id: $id) {
            title, description, extraFields
        }
        tags(model: "report_observation_link", id: $id) {
            tags
        }
        extraFieldSpec(where:{targetModel:{_eq:"reporting.Observation"}}) {
            internalName, type
        }
    }
`);
const SET = gql(`
    mutation SET_REPORT_OBSERVATION_LINK(
        $id:bigint!,
        $title:String!,
        $description:String!,
        $tags:[String!]!,
        $extraFields:jsonb!,
    ) {
        update_reporting_reportobservationlink_by_pk(pk_columns:{id:$id}, _set:{
            title: $title,
            description: $description,
            extraFields: $extraFields,
        }) {
            id
        }
        setTags(model: "report_observation_link", id: $id, tags: $tags) {
            tags
        }
    }
`);
const ReportObservationLinkHandler = simpleModelHandler(
  GET,
  SET,
  (doc, res) => {
    const obj = res.reporting_reportobservationlink_by_pk;
    if (!obj) throw new Error("No object");
    const plain_fields = doc.get("plain_fields", Y.Map);
    plain_fields.set("title", obj.title);
    htmlToYjs(obj.description, doc.get("description", Y.XmlFragment));
    tagsToYjs(res.tags.tags, doc.get("tags", Y.Map));
    extraFieldsToYdoc(res.extraFieldSpec, doc, obj.extraFields);
  },
  (doc, id) => {
    const plainFields = doc.get("plain_fields", Y.Map);
    const extraFields = extraFieldsFromYdoc(doc);
    return {
      id,
      title: plainFields.get("title") ?? "",
      description: yjsToHtml(doc.get("description", Y.XmlFragment)),
      tags: yjsToTags(doc.get("tags", Y.Map)),
      extraFields
    };
  }
);
const HANDLERS = /* @__PURE__ */ new Map([
  ["observation", ObservationHandler],
  ["report_observation_link", ReportObservationLinkHandler],
  ["finding", FindingHandler],
  ["report_finding_link", ReportFindingLinkHandler],
  ["report", ReportHandler]
]);
if (process.argv.length !== 5 || process.argv.includes("-h", 2) || process.argv.includes("--help", 2)) {
  console.error("Usage: stress_test (num_workers) (model_type) (model_id)");
  process.exit(2);
}
const numWorkers = parseInt(process.argv[2]);
const modelType = process.argv[3];
const modelId = parseInt(process.argv[4]);
if (numWorkers !== numWorkers || modelId !== modelId) {
  throw new Error("Invalid argument");
}
const handler = HANDLERS.get(modelType);
if (handler === void 0)
  throw new Error("Unrecognized model type");
const gqlClient = createApolloClient();
let stop = false;
process.on("SIGINT", () => {
  stop = true;
  console.log("Stopping...");
});
const worker = async () => {
  const doc = await handler.load(gqlClient, modelId);
  while (!stop) {
    await handler.save(gqlClient, modelId, doc);
  }
};
const workers = [];
console.log("Starting... Ctrl+C to stop");
for (let i = 0; i < numWorkers; i++) {
  workers.push(worker());
}
await Promise.all(workers);
process.exit(0);
//# sourceMappingURL=index.js.map
