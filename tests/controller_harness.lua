-- SPDX-License-Identifier: MIT
-- Small WoW API stand-in: exercise the actual published commands, not a game.
local actions = {W = 'MOVEFORWARD', ['1'] = 'ACTIONBUTTON1', PAD2 = 'CAMERAZOOMIN'}
local cvars, settings, saved, reloaded = {}, {}, false, false
function SetBinding(key, value)
  assert(key:find('PAD', 1, true), 'recipe tried to write a non-controller key')
  actions[key] = value
  return true
end
function GetBindingAction(key) return actions[key] or '' end
function GetCVar(key) return cvars[key] end
CPAPI = {SaveBindings = function() saved = true; return true end}
local active = {
  Generator = {Triggers = {
    PADLSHOULDER = {[''] = 'ACTIONBUTTON2', ['SHIFT-'] = 'MULTIACTIONBAR1BUTTON2'},
    PADRSHOULDER = {[''] = 'ACTIONBUTTON1', ['CTRL-'] = 'MULTIACTIONBAR1BUTTON1'},
  }},
  GetPresetBindings = function()
    return {PAD1 = 'JUMP', PAD2 = 'ACTIONBUTTON5', PAD3 = 'ACTIONBUTTON3', PAD4 = 'ACTIONBUTTON4',
            PADLSTICK = 'CAMERAORSELECTORMOVE', PADRSTICK = 'TURNORACTION'}
  end,
}
local gamepad = {Active = active,
  FlattenBindings = function(_, map) return map end,
  GetBindings = function() return {PAD2 = actions.PAD2} end}
local db = setmetatable({Gamepad = gamepad,
  SetCVar = function(_, key, value) cvars[key] = value end}, {
    __call = function(_, key, value) settings[key] = value end})
ConsolePort = {GetData = function() return db end}
for line in io.lines(arg[1]) do
  if line:sub(1, 5) == '/run ' then
    local code, error = load(line:sub(6))
    assert(code, error)
    code()
  elseif line == '/reload' then
    assert(saved, 'reload before bindings were saved')
    reloaded = true
  elseif line ~= '' then
    assert(line:sub(1, 1) == '#', 'unsupported command')
  end
end
assert(actions.W == 'MOVEFORWARD' and actions['1'] == 'ACTIONBUTTON1', 'keyboard bindings changed')
assert(actions.PAD1 == 'JUMP' and actions.PAD2 == 'ACTIONBUTTON5' and actions.PAD3 == 'INTERACTTARGET')
assert(actions.PAD4 == 'ACTIONBUTTON4' and actions.PADLSHOULDER == 'ACTIONBUTTON2' and actions.PADRSHOULDER == 'ACTIONBUTTON1')
assert(actions.PADFORWARD == 'TOGGLEGAMEMENU' and actions.PADBACK == 'OPENALLBAGS')
assert(cvars.GamePadEmulateShift == 'PADLTRIGGER' and cvars.GamePadEmulateCtrl == 'PADRTRIGGER')
assert(cvars.GamePadEmulateAlt == 'none' and cvars.GamePadEmulateTapWindowMs == 350)
assert(cvars.GamePadCursorLeftClick == 'PADLSTICK' and cvars.GamePadCursorRightClick == 'PADRSTICK')
assert(cvars.SoftTargetInteract == 3 and cvars.GamePadEnable == 1)
assert(settings['Settings/UICursorCancel'] == 'PAD2' and settings['Settings/UICursorLeftClick'] == 'PAD1')
assert(settings['Settings/gameMenuAccept'] == 'PAD1' and settings['Settings/gameMenuReturn'] == 'PAD2')
assert(settings['Settings/gameMenuSwitch'] == 'PADRSHOULDER' and settings['Settings/gameMenuCustomSet'] == true)
assert(GNControllerBackup.PAD2 == 'CAMERAZOOMIN' and saved and reloaded)
print('Controller recipe passed the simulated API checks; live UI behavior still needs manual testing.')
