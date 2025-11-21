-- Neato Bridge for Bizhawk
-- Acts as a server to communicate with the Python Brain

local socket = require("socket.core")

local HOST = "127.0.0.1"
local PORT = 8086
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
    print("Server started v17 (Port " .. PORT .. "). Waiting for connection...")
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
            -- Verbose logging for user visibility
            if command ~= "GET_STATE" then -- Don't spam GET_STATE, it happens every frame
                 -- print("Lua Received: " .. command)
            end
            
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
                
                -- Read Mario's Position (SMW specific)
                -- 0x94 = Mario X (2 bytes)
                -- 0x96 = Mario Y (2 bytes)
                local mario_x = memory.read_u16_le(0x94)
                local mario_y = memory.read_u16_le(0x96)
                
                -- Read Game State
                -- 0x100 = Game Mode (u8)
                -- 0x13BF = Level Index (u8)
                -- 0x1493 = End Level Timer (u8) - Non-zero means level finished
                -- 0x71   = Player Animation (u8) - 9 means dead
                local game_mode = memory.read_u8(0x100)
                local level_index = memory.read_u8(0x13BF)
                local end_timer = memory.read_u8(0x1493)
                local anim_state = memory.read_u8(0x71)
                
                send_data(string.format("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d", x, y, w, h, bx, by, mario_x, mario_y, game_mode, level_index, end_timer, anim_state))
            elseif string.sub(command, 1, 4) == "ACT:" then
                -- Parse buttons
                -- Format: ACT:A,B,Up
                local btn_str = string.sub(command, 5)
                local buttons = {}
                for btn in string.gmatch(btn_str, "([^,]+)") do
                    buttons[btn] = true
                end
                
                joypad.set(buttons, 1)
                emu.frameadvance()
                send_data("ACT_OK")
            elseif command == "RESET" then
                savestate.loadslot(1)  -- Load slot 1 (1-indexed for slots)
                emu.frameadvance()  -- Let the save state fully apply
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
