
// db-container/mongo-setup.sh
#!/bin/bash
# Setup script for MongoDB container

# Enable MongoDB authentication if needed
# mongod --auth

# Set environment variables
export MONGO_INITDB_DATABASE="together"

# Start MongoDB with appropriate settings
exec mongod --bind_ip_all