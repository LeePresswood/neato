-- Neato Bridge for Bizhawk
-- Acts as a server to communicate with the Python Brain

local socket = require("socket.core")

local HOST = "127.0.0.1"
local PORT = 8080
local server = nil
local client = nil

-- Initialize Server
function init_server()
    print("Attempting to start server on " .. HOST .. ":" .. PORT)
    server = socket.tcp()
    local res, err = server:bind(HOST, PORT)
    if not res then
        print("Failed to bind: " .. err)
        return false
    end
    server:listen(1)
    server:settimeout(0) -- Non-blocking
    print("Server started. Waiting for connection...")
    return true
end

-- Accept Client Connection
function accept_client()
    if server == nil then return end
    local new_client, err = server:accept()
    if new_client then
        client = new_client
        client:settimeout(0)
        print("Client connected!")
    end
end

-- Receive Data
function receive_data()
    if client == nil then return nil end
    local line, err = client:receive("*l") -- Read line
    if err then
        if err ~= "timeout" then
            print("Client disconnected: " .. err)
            client = nil
        end
        return nil
    end
    return line
end

-- Send Data
function send_data(data)
    if client == nil then return end
    local res, err = client:send(data .. "\n")
    if not res then
        print("Failed to send: " .. err)
        client = nil
    end
end

-- Main Loop
if init_server() then
    while true do
        accept_client()
        
        local command = receive_data()
        if command then
            -- print("Received: " .. command)
            
            if command == "GET_STATE" then
                -- TODO: Capture screen or RAM
                -- For now, just send a dummy response
                send_data("STATE_OK")
            elseif command == "ACT" then
                -- TODO: Press buttons
                send_data("ACT_OK")
                emu.frameadvance()
            elseif command == "RESET" then
                emu.softreset()
                send_data("RESET_OK")
            else
                send_data("UNKNOWN_CMD")
            end
        else
            -- If no command, just advance frame to keep game running?
            -- Or pause? For now, let's just yield
            emu.yield()
        end
    end
end
