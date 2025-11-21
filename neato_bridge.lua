-- Neato Bridge for Bizhawk
-- Acts as a server to communicate with the Python Brain

local socket = require("socket.core")

local HOST = "127.0.0.1"
local PORT = 8083
local server = nil
local tcp_client = nil -- Renamed from client to avoid shadowing Bizhawk API

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
    print("Server started v5 (Port " .. PORT .. "). Waiting for connection...")
    return true
end

-- Accept Client Connection
function accept_client()
    if server == nil then return end
    local new_client, err = server:accept()
    if new_client then
        tcp_client = new_client
        tcp_client:settimeout(0)
        print("Client connected!")
    end
end

-- Receive Data
function receive_data()
    if tcp_client == nil then return nil end
    local line, err = tcp_client:receive("*l") -- Read line
    if err then
        if err ~= "timeout" then
            print("Client disconnected: " .. err)
            tcp_client = nil
        end
        return nil
    end
    return line
end

-- Send Data
function send_data(data)
    if tcp_client == nil then return end
    local res, err = tcp_client:send(data .. "\n")
    if not res then
        print("Failed to send: " .. err)
        tcp_client = nil
    end
end

-- Cleanup on exit
event.onexit(function()
    print("Shutting down server...")
    if tcp_client then tcp_client:close() end
    if server then server:close() end
end)

-- Main Loop
if init_server() then
    while true do
        accept_client()
        
        local command = receive_data()
        if command then
            -- print("Received: " .. command)
            
            if command == "GET_STATE" then
                -- Return window coordinates for Python to capture
                local x = 0
                local y = 0
                if client.xpos then x = client.xpos() end
                if client.ypos then y = client.ypos() end
                
                local w = 256
                local h = 224
                if client.screenwidth then w = client.screenwidth() end
                if client.screenheight then h = client.screenheight() end
                
                -- Also get border info to help crop
                local bx = 0
                local by = 0
                if client.borderwidth then bx = client.borderwidth() end
                if client.borderheight then by = client.borderheight() end
                
                send_data(string.format("%d,%d,%d,%d,%d,%d", x, y, w, h, bx, by))
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
