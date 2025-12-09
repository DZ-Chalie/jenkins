import NextAuth from "next-auth";
import CognitoProvider from "next-auth/providers/cognito";

const handler = NextAuth({
    providers: [
        CognitoProvider({
            clientId: process.env.COGNITO_CLIENT_ID ?? "",
            clientSecret: process.env.COGNITO_CLIENT_SECRET ?? "",
            issuer: process.env.COGNITO_ISSUER ?? "",
            checks: ["state", "nonce"],
            authorization: {
                params: {
                    prompt: "select_account",
                }
            },
        }),
    ],
    session: {
        strategy: "jwt",
    },
    callbacks: {
        async jwt({ token, account, profile }) {
            // Save user info from profile to token
            if (account && profile) {
                token.sub = profile.sub;
                token.email = profile.email;
                token.name = profile.name || profile.email?.split('@')[0];
            }
            return token;
        },
        async session({ session, token }) {
            // Pass user info from token to session
            if (token) {
                session.user = {
                    ...session.user,
                    email: token.email as string,
                    name: token.name as string,
                };
            }
            return session;
        },
    },
    events: {
        async signOut({ token }) {
            // This will be called when user signs out
            // The actual Cognito logout will be handled by the custom signout redirect
        },
    },
    debug: true,
});

export { handler as GET, handler as POST };
