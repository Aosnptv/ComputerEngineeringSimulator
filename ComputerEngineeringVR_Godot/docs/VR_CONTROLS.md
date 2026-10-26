# VR controls

Native Godot OpenXR is used; SteamVR should be the active PC OpenXR runtime. The player rig contains XROrigin3D, XRCamera3D, left/right XRController3D nodes, visible controller hands, and controller rays. Desired bindings are grip/squeeze for grab, trigger for activate/UI, left trackpad/thumbstick for movement, right trackpad/thumbstick for snap turn/teleport, and menu for pause. Vive and Index runtime binding verification requires their physical controllers and remains NOT TESTED.

The code preserves the persistent XR origin across room changes and provides recenter infrastructure. Snap turn defaults to 45° and settings support 30°. Standing/seated height settings are stored. Full runtime binding/action-map and comfort acceptance must be completed in Godot with hardware.

