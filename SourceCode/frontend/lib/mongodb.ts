// This approach is taken from https://github.com/vercel/next.js/tree/canary/examples/with-mongodb
import { MongoClient } from "mongodb";

if (!process.env.MONGODB_URI) {
    // In production (build time), we might not have the env var yet.
    // We can warn or just let it fail at runtime if it's truly missing.
    // For build safety, we can default to empty string but throw if used.
    if (process.env.NODE_ENV === "production") {
        console.warn('Invalid/Missing environment variable: "MONGODB_URI"');
    } else {
        throw new Error('Invalid/Missing environment variable: "MONGODB_URI"');
    }
}

const uri = process.env.MONGODB_URI || "mongodb://localhost:27017/dummy";
const options = {};

let client;
let clientPromise: Promise<MongoClient>;

if (process.env.NODE_ENV === "development") {
    // In development mode, use a global variable so that the value
    // is preserved across module reloads caused by HMR (Hot Module Replacement).
    let globalWithMongo = global as typeof globalThis & {
        _mongoClientPromise?: Promise<MongoClient>;
    };

    if (!globalWithMongo._mongoClientPromise) {
        client = new MongoClient(uri, options);
        globalWithMongo._mongoClientPromise = client.connect();
    }
    clientPromise = globalWithMongo._mongoClientPromise;
} else {
    // In production mode, it's best to not use a global variable.
    client = new MongoClient(uri, options);
    clientPromise = client.connect();
}

// Export a module-scoped MongoClient promise. By doing this in a
// separate module, the client can be shared across functions.
export default clientPromise;
