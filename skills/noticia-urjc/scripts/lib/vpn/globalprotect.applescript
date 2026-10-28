-- Pulsa en GlobalProtect el botón de conectar o desconectar (argumento: conectar | desconectar), o
-- dice qué botón hay sin pulsar nada (estado): «Disconnect» es que el túnel está arriba.
-- Lo usa conectar.sh; necesita permiso de Accesibilidad para la aplicación que lo ejecuta.
--
-- Lo comprobado el 2026-10-28 (GlobalProtect 6.2.8, en inglés):
-- - el icono de la barra de menús abre y cierra el panel: si ya está abierto, no se pulsa;
-- - solo cuentan los botones, y por su etiqueta exacta: el panel también tiene textos e imágenes que
--   contienen la palabra («Not Connected», «GlobalProtect Disconnected»), y pulsar uno no hace nada;
-- - la etiqueta está en el atributo AXTitle; el de desconectar no tiene ni nombre ni descripción.
on run argv
  set quiero to item 1 of argv
  if quiero is "desconectar" then
    set etiquetas to {"Disconnect", "Desconectar"}
  else
    set etiquetas to {"Connect", "Conectar"}
  end if
  tell application "System Events" to tell process "GlobalProtect"
    repeat 3 times
      if exists window 1 then exit repeat
      click menu bar item 1 of menu bar 2
      delay 1.5
    end repeat
    if not (exists window 1) then return "sin panel: el icono de la barra de menús no lo abre"
    if quiero is "estado" then
      set vistos to {}
      repeat with b in (every button of window 1)
        try
          set end of vistos to (value of attribute "AXTitle" of b as text)
        end try
      end repeat
      key code 53
      set AppleScript's text item delimiters to " | "
      return "botones: " & (vistos as text)
    end if
    set vistos to {}
    repeat with b in (every button of window 1)
      set n to ""
      try
        set n to (value of attribute "AXTitle" of b as text)
      end try
      if n is "" or n is "missing value" then
        try
          set n to (name of b as text)
        end try
      end if
      set end of vistos to n
      if etiquetas contains n then
        click b
        return "pulsado"
      end if
    end repeat
    key code 53
    set AppleScript's text item delimiters to " | "
    return "sin botón: " & (vistos as text)
  end tell
end run
