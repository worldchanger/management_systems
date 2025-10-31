#!/bin/bash
# Local Rails Apps Management Script
# Manages cigar, tobacco, and whiskey Rails applications locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CIGAR_DIR="$SCRIPT_DIR/cigar-management-system"
TOBACCO_DIR="$SCRIPT_DIR/tobacco-management-system"
WHISKEY_DIR="$SCRIPT_DIR/whiskey-management-system"
QA_TEST_REPO_DIR="$SCRIPT_DIR/qa-test-repo"

CIGAR_PORT=3001
TOBACCO_PORT=3002
WHISKEY_PORT=3003
QA_TEST_REPO_PORT=3004

CIGAR_PID_FILE="$CIGAR_DIR/tmp/pids/server.pid"
TOBACCO_PID_FILE="$TOBACCO_DIR/tmp/pids/server.pid"
WHISKEY_PID_FILE="$WHISKEY_DIR/tmp/pids/server.pid"
QA_TEST_REPO_PID_FILE="$QA_TEST_REPO_DIR/tmp/pids/server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if app is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to start an app
start_app() {
    local app_name=$1
    local app_dir=$2
    local port=$3
    local pid_file=$4
    
    if is_running "$pid_file"; then
        echo -e "${YELLOW}⚠️  $app_name is already running on port $port${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🚀 Preparing $app_name on port $port...${NC}"
    cd "$app_dir"

    # Ensure dependencies are up to date
    bundle check || bundle install

    # Prepare database and assets
    echo -e "${BLUE}   📦 Preparing database...${NC}"
    RAILS_ENV=development bin/rails db:prepare > /dev/null 2>&1 || {
        echo -e "${YELLOW}   ⚠️  Database prep had issues, continuing...${NC}"
    }
    
    echo -e "${BLUE}   🎨 Compiling assets...${NC}"
    yarn build:css > /dev/null 2>&1 || {
        echo -e "${YELLOW}   ⚠️  Asset compilation skipped${NC}"
    }
    
    # Run database migrations
    echo -e "${BLUE}   🧱 Running migrations...${NC}"
    bin/rails db:migrate RAILS_ENV=development > /dev/null 2>&1 || {
        echo -e "${YELLOW}   ⚠️  Migration issues, continuing...${NC}"
    }

    # Finally start the server (assets compile on-demand in development)
    echo -e "${BLUE}   🌟 Starting server...${NC}"
    bin/rails server -p $port -d
    sleep 3
    
    if is_running "$pid_file"; then
        echo -e "${GREEN}✅ $app_name started successfully on http://localhost:$port${NC}"
    else
        echo -e "${RED}❌ Failed to start $app_name${NC}"
        return 1
    fi
}

# Function to stop an app
stop_app() {
    local app_name=$1
    local pid_file=$2
    
    if ! is_running "$pid_file"; then
        echo -e "${YELLOW}⚠️  $app_name is not running${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🛑 Stopping $app_name...${NC}"
    local pid=$(cat "$pid_file")
    kill $pid
    sleep 1
    
    # Force kill if still running
    if ps -p $pid > /dev/null 2>&1; then
        kill -9 $pid 2>/dev/null || true
    fi
    
    rm -f "$pid_file"
    echo -e "${GREEN}✅ $app_name stopped${NC}"
}

# Function to restart an app
restart_app() {
    local app_name=$1
    local app_dir=$2
    local port=$3
    local pid_file=$4
    
    stop_app "$app_name" "$pid_file"
    sleep 1
    start_app "$app_name" "$app_dir" "$port" "$pid_file"
}

# Function to show status
show_status() {
    echo -e "${BLUE}📊 Rails Apps Status:${NC}"
    echo ""
    
    if is_running "$CIGAR_PID_FILE"; then
        echo -e "  ${GREEN}●${NC} Cigar Management    - http://localhost:$CIGAR_PORT"
    else
        echo -e "  ${RED}○${NC} Cigar Management    - Stopped"
    fi
    
    if is_running "$TOBACCO_PID_FILE"; then
        echo -e "  ${GREEN}●${NC} Tobacco Management  - http://localhost:$TOBACCO_PORT"
    else
        echo -e "  ${RED}○${NC} Tobacco Management  - Stopped"
    fi
    
    if is_running "$WHISKEY_PID_FILE"; then
        echo -e "  ${GREEN}●${NC} Whiskey Management  - http://localhost:$WHISKEY_PORT"
    else
        echo -e "  ${RED}○${NC} Whiskey Management  - Stopped"
    fi
    echo ""
}

# Main command handling
case "${1:-}" in
    start)
        case "${2:-all}" in
            cigar)
                start_app "Cigar Management" "$CIGAR_DIR" "$CIGAR_PORT" "$CIGAR_PID_FILE"
                ;;
            tobacco)
                start_app "Tobacco Management" "$TOBACCO_DIR" "$TOBACCO_PORT" "$TOBACCO_PID_FILE"
                ;;
            whiskey)
                start_app "Whiskey Management" "$WHISKEY_DIR" "$WHISKEY_PORT" "$WHISKEY_PID_FILE"
                ;;
            qa-test-repo)
                start_app "QA Test Repo" "$QA_TEST_REPO_DIR" "$QA_TEST_REPO_PORT" "$QA_TEST_REPO_PID_FILE"
                ;;
            all)
                start_app "Cigar Management" "$CIGAR_DIR" "$CIGAR_PORT" "$CIGAR_PID_FILE"
                start_app "Tobacco Management" "$TOBACCO_DIR" "$TOBACCO_PORT" "$TOBACCO_PID_FILE"
                start_app "Whiskey Management" "$WHISKEY_DIR" "$WHISKEY_PORT" "$WHISKEY_PID_FILE"
                start_app "QA Test Repo" "$QA_TEST_REPO_DIR" "$QA_TEST_REPO_PORT" "$QA_TEST_REPO_PID_FILE"
                ;;
            *)
                echo -e "${RED}Unknown app: $2${NC}"
                echo "Usage: $0 start [cigar|tobacco|whiskey|qa-test-repo|all]"
                exit 1
                ;;
        esac
        ;;
    
    stop)
        case "${2:-all}" in
            cigar)
                stop_app "Cigar Management" "$CIGAR_PID_FILE"
                ;;
            tobacco)
                stop_app "Tobacco Management" "$TOBACCO_PID_FILE"
                ;;
            whiskey)
                stop_app "Whiskey Management" "$WHISKEY_PID_FILE"
                ;;
            qa-test-repo)
                stop_app "QA Test Repo" "$QA_TEST_REPO_PID_FILE"
                ;;
            all)
                stop_app "Cigar Management" "$CIGAR_PID_FILE"
                stop_app "Tobacco Management" "$TOBACCO_PID_FILE"
                stop_app "Whiskey Management" "$WHISKEY_PID_FILE"
                stop_app "QA Test Repo" "$QA_TEST_REPO_PID_FILE"
                ;;
            *)
                echo -e "${RED}Unknown app: $2${NC}"
                echo "Usage: $0 stop [cigar|tobacco|whiskey|qa-test-repo|all]"
                exit 1
                ;;
        esac
        ;;
    
    restart)
        case "${2:-all}" in
            cigar)
                restart_app "Cigar Management" "$CIGAR_DIR" "$CIGAR_PORT" "$CIGAR_PID_FILE"
                ;;
            tobacco)
                restart_app "Tobacco Management" "$TOBACCO_DIR" "$TOBACCO_PORT" "$TOBACCO_PID_FILE"
                ;;
            whiskey)
                restart_app "Whiskey Management" "$WHISKEY_DIR" "$WHISKEY_PORT" "$WHISKEY_PID_FILE"
                ;;
            qa-test-repo)
                restart_app "QA Test Repo" "$QA_TEST_REPO_DIR" "$QA_TEST_REPO_PORT" "$QA_TEST_REPO_PID_FILE"
                ;;
            all)
                restart_app "Cigar Management" "$CIGAR_DIR" "$CIGAR_PORT" "$CIGAR_PID_FILE"
                restart_app "Tobacco Management" "$TOBACCO_DIR" "$TOBACCO_PORT" "$TOBACCO_PID_FILE"
                restart_app "Whiskey Management" "$WHISKEY_DIR" "$WHISKEY_PORT" "$WHISKEY_PID_FILE"
                restart_app "QA Test Repo" "$QA_TEST_REPO_DIR" "$QA_TEST_REPO_PORT" "$QA_TEST_REPO_PID_FILE"
                ;;
            *)
                echo -e "${RED}Unknown app: $2${NC}"
                echo "Usage: $0 restart [cigar|tobacco|whiskey|qa-test-repo|all]"
                exit 1
                ;;
        esac
        ;;
    
    status)
        show_status
        ;;
    
    *)
        echo "Rails Apps Local Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status} [app]"
        echo ""
        echo "Commands:"
        echo "  start [app]   - Start one or all apps"
        echo "  stop [app]    - Stop one or all apps"
        echo "  restart [app] - Restart one or all apps"
        echo "  status        - Show status of all apps"
        echo ""
        echo "Apps: cigar, tobacco, whiskey, all (default)"
        echo ""
        echo "Examples:"
        echo "  $0 start              # Start all apps"
        echo "  $0 start whiskey      # Start only whiskey app"
        echo "  $0 stop all           # Stop all apps"
        echo "  $0 restart cigar      # Restart cigar app"
        echo "  $0 status             # Show status"
        exit 1
        ;;
esac
