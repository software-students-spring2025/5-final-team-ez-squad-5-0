// db-container/init-mongo.js
// MongoDB initialization script for Together app

// Switch to the 'together' database
db = db.getSiblingDB('together');

// --- Core Collections ---
const coreCols = [
    'users',
    'events',
    'messages',
    'scheduled_messages',
    'analyzed_messages',
    'relationship_metrics',
    'daily_question'
];
coreCols.forEach(col => {
    if (!db.getCollectionNames().includes(col)) {
        db.createCollection(col);
    }
});

// --- Indexes ---
db.users.createIndex({ email: 1 }, { unique: true });
db.events.createIndex({ user_id: 1 });
db.events.createIndex({ start_time: 1 });
db.messages.createIndex({ sender_id: 1 });
db.messages.createIndex({ receiver_id: 1 });
db.scheduled_messages.createIndex({ scheduled_time: 1 });
db.scheduled_messages.createIndex({ sender_id: 1 });
db.daily_question.createIndex({ date: 1 }, { unique: true });

// (Optional) Seed two test users
try {
    db.users.insertOne({
        name: "Test User",
        email: "test@example.com",
        password_hash: "$2b$12$K8PVqOGX9jCNSvv3xM2qZ.TQP0XR.fjrLPJYEIfMEmMuGTzwYMj2m",
        partner_email: "partner@example.com",
        partner_id: null,
        email_notifications: true,
        created_at: new Date()
    });
    db.users.insertOne({
        name: "Partner User",
        email: "partner@example.com",
        password_hash: "$2b$12$K8PVqOGX9jCNSvv3xM2qZ.TQP0XR.fjrLPJYEIfMEmMuGTzwYMj2m",
        partner_email: "test@example.com",
        partner_id: null,
        email_notifications: true,
        created_at: new Date()
    });
    print("Sample users created.");
} catch (e) {
    print("Sample users exist or could not be created: " + e.message);
}

print("MongoDB init complete.");