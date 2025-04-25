// db-container/init-mongo.js
// MongoDB initialization script that runs when the container starts

// Switch to the 'together' database (creates it if it doesn't exist)
db = db.getSiblingDB('together');

// Create collections
db.createCollection('users');
db.createCollection('events');
db.createCollection('messages');
db.createCollection('scheduled_messages'); // New collection for scheduled messages
db.createCollection('analyzed_messages');
db.createCollection('relationship_metrics');
db.createCollection('daily_question');

// Create indexes for better query performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.events.createIndex({ "user_id": 1 });
db.events.createIndex({ "start_time": 1 });
db.messages.createIndex({ "sender_id": 1 });
db.messages.createIndex({ "receiver_id": 1 });
db.scheduled_messages.createIndex({ "scheduled_time": 1 }); // Index for efficient querying by time
db.scheduled_messages.createIndex({ "sender_id": 1 });
db.daily_question.createIndex({ "date": 1 }, { unique: true });

// Insert sample users (optional, for testing)
try {
  // First user
  db.users.insertOne({
    name: "Test User",
    email: "test@example.com",
    password_hash: "$2b$12$K8PVqOGX9jCNSvv3xM2qZ.TQP0XR.fjrLPJYEIfMEmMuGTzwYMj2m", // Password: password123
    partner_email: "partner@example.com",
    partner_id: null,
    email_notifications: true,
    created_at: new Date()
  });
  print("Created test user: test@example.com / password123");
  
  // Second user (partner)
  db.users.insertOne({
    name: "Partner User",
    email: "partner@example.com",
    password_hash: "$2b$12$K8PVqOGX9jCNSvv3xM2qZ.TQP0XR.fjrLPJYEIfMEmMuGTzwYMj2m", // Password: password123
    partner_email: "test@example.com",
    partner_id: null,
    email_notifications: true,
    created_at: new Date()
  });
  print("Created partner user: partner@example.com / password123");
} catch (e) {
  print("Test users already exist or could not be created: " + e.message);
}

print("MongoDB initialization complete!");