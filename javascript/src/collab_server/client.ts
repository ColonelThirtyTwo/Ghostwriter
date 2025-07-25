// Apollo's lib is commonjs and ts doesn't see its exports, so work around it.
import * as apollo from "@apollo/client/core";
const { ApolloClient, createHttpLink, InMemoryCache } = apollo;

import { setContext } from "@apollo/client/link/context";
import { env } from "node:process";

export function createApolloClient() {
    const httpLink = createHttpLink({
        uri: "http://graphql_engine:8080/v1/graphql",
    });

    const authLink = setContext((_, { headers }) => {
        return {
            headers: {
                ...headers,
                "x-hasura-admin-secret": env[
                    "HASURA_GRAPHQL_ADMIN_SECRET"
                ],
            },
        };
    });

    return new ApolloClient({
        link: authLink.concat(httpLink),
        cache: new InMemoryCache(),
        defaultOptions: {
            query: {
                fetchPolicy: "no-cache",
                errorPolicy: "all",
            },
            watchQuery: {
                fetchPolicy: "no-cache",
                errorPolicy: "all",
            },
        },
    });
}
