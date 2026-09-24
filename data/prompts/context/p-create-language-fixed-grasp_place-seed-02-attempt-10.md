## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0919 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3153 | 0.77 | ❌ rejected |
| 8 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4332 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4051 | 0.95 | ❌ rejected |
| 6 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4079 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.092) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
- id: transport
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.092
- **task_score** (E): 0.386
- **fitness_score**: 0.662  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2050 |
| descend | 1.00 | 1.00 | 0.0508 |
| grasp | 1.00 | 1.00 | 0.0115 |
| transport | 0.33 | 1.00 | 0.2570 |
| place_descend | 0.67 | 1.00 | 0.0364 |
| release | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.100) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.490, -0.014, 0.100)→(0.488, -0.015, 0.049) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 9.421 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.049)→(0.480, -0.015, 0.041) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.136 | 0.177 |
| transport | approach | 0.33 / step_budget | (0.480, -0.015, 0.041)→(0.599, 0.134, 0.204) | (0.493, -0.015, 0.026)→(0.607, 0.134, 0.180) | 0.281→0.053 | 1.00 / 25.333 | 94.786 | 0.496 |
| place_descend | descend | 0.67 / step_budget | (0.599, 0.134, 0.204)→(0.615, 0.155, 0.180) | (0.607, 0.134, 0.180)→(0.622, 0.147, 0.092) | 0.053→0.080 | 1.00 / 20.333 | 91001.570 | 0.820 |
| release | release | 1.00 / step_budget | (0.615, 0.155, 0.180)→(0.609, 0.153, 0.200) | (0.622, 0.147, 0.092)→(0.615, 0.144, 0.022) | 0.080→0.149 | 1.00 / 3.000 | 0.152 | 0.873 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.547
- phase_score: 0.513
- phase_breakdown.transport_arc_score: 0.309
- phase_breakdown.approach_1_score: 0.271
- phase_breakdown.release_1_score: 0.602
- phase_breakdown.descend_1_score: 0.889
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.547
- **Median Q (composite search score)**: 0.059
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.347


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34928,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.07149,"approach.speed":0.06959,"descend.grasp_z_offset":0.0157,"descend.speed":0.0837,"place_descend.place_height_offset":0.00086,"place_descend.place_speed":0.0179,"transport.arc_height":0.096,"transport.placement_z_offset":0.04244,"transport.transport_speed":0.03541},"optimized_scores":{"best_composite_score":0.04138,"best_fitness_score":0.61138,"best_task_score":0.28726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3475.0,"contact_point_centroid":[0.6011,0.09741,-0.00234],"force_p95":0.12449,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86545,"mean_force":0.1366,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5864,0.1159,0.22567]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47316,-0.01977,-0.00138],"force_p95":0.42303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48998,"mean_force":0.1329,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.46258,-0.01971,0.04375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.58748,0.12765,0.23431],"force_p95":0.2319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3363,"mean_force":0.1815,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58173,0.10959,0.2387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12955.0,"contact_point_centroid":[0.49229,0.02952,0.15365],"force_p95":0.12405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30592,"mean_force":0.07608,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48893,0.01067,0.15175]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14370.0,"contact_point_centroid":[0.493,-0.00732,0.15342],"force_p95":0.1098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29631,"mean_force":0.07007,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.4896,0.01138,0.15222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":396.0,"contact_point_centroid":[0.58751,0.09285,0.23433],"force_p95":0.16204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28408,"mean_force":0.08713,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58176,0.10975,0.23808]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02008,-0.00205],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17812,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46489,-0.01959,0.0436]},{"body_a":"world","body_b":"grasp_target","contact_count":2372.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48616,-0.00911,0.20543]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47167,-0.01912,0.08058]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60111,0.09742,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58655,0.11882,0.22317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5079.0,"contact_point_centroid":[0.46356,-0.00031,0.04534],"force_p95":0.06616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09902,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46379,-0.01956,0.0425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5393.0,"contact_point_centroid":[0.46343,-0.03881,0.04484],"force_p95":0.06514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08337,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46379,-0.01956,0.0425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3485.0,"contact_point_centroid":[0.58706,0.11614,0.22761],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01595,"mean_force":0.01053,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58663,0.11613,0.22541]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.58941,0.1194,0.22135],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00997,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58886,0.11939,0.21907]}],"total_contact_groups":14},"final_pose_error":0.06506,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60111,0.09742,0.01602],"final_tcp_position":[0.59006,0.11963,0.2218],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.51736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2372.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47398,-0.01857,0.11108],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47146,-0.01974,0.05029],"tcp_start":[0.47398,-0.01857,0.11108],"tcp_to_object_dist_end":0.02472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.0197,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13552,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12272.0,"raw_peak_contact_force":0.17812,"subtask_id":"grasp_1","tcp_end":[0.46376,-0.01956,0.04247],"tcp_start":[0.47146,-0.01974,0.05029],"tcp_to_object_dist_end":0.02072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58816,0.10882,0.21272],"object_pos_start":[0.47608,-0.0197,0.02581],"object_to_goal_dist_end":0.07018,"object_to_goal_dist_start":0.28826,"object_z_max":0.21346,"peak_contact_force":0.15434,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27402.0,"raw_peak_contact_force":0.48998,"subtask_id":"transport_arc","tcp_end":[0.58178,0.10853,0.24148],"tcp_start":[0.46376,-0.01956,0.04247],"tcp_to_object_dist_end":0.02946,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60111,0.09742,0.01602],"object_pos_start":[0.58816,0.10882,0.21272],"object_to_goal_dist_end":0.18711,"object_to_goal_dist_start":0.07018,"object_z_max":0.21272,"peak_contact_force":273004.51736,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7554.0,"raw_peak_contact_force":1.86545,"tcp_end":[0.59006,0.11963,0.2218],"tcp_start":[0.58178,0.10853,0.24148],"tcp_to_object_dist_end":0.20727,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60111,0.09742,0.01602],"object_pos_start":[0.60111,0.09742,0.01602],"object_to_goal_dist_end":0.18711,"object_to_goal_dist_start":0.18711,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58525,0.11848,0.24303],"tcp_start":[0.59006,0.11963,0.2218],"tcp_to_object_dist_end":0.22854,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07692,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05559,"approach.speed":0.0575,"descend.grasp_z_offset":0.01122,"descend.speed":0.05117,"place_descend.place_height_offset":0.00954,"place_descend.place_speed":0.07461,"transport.arc_height":0.07132,"transport.placement_z_offset":0.03138,"transport.transport_speed":0.0127},"optimized_scores":{"best_composite_score":0.1758,"best_fitness_score":0.7458,"best_task_score":0.54676},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":251.0,"contact_point_centroid":[0.61244,0.19525,-0.00454],"force_p95":0.91011,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07451,"mean_force":0.27663,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61737,0.20253,0.12301]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.45711,-0.02444,-0.00139],"force_p95":0.39837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45879,"mean_force":0.16828,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.44627,-0.02482,0.04005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13894.0,"contact_point_centroid":[0.61629,0.2095,0.13121],"force_p95":0.10369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33185,"mean_force":0.07088,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61178,0.19054,0.1303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18545.0,"contact_point_centroid":[0.50749,0.03528,0.12513],"force_p95":0.0821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25915,"mean_force":0.05535,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50612,0.05425,0.12366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16858.0,"contact_point_centroid":[0.50926,0.07545,0.12654],"force_p95":0.08745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2439,"mean_force":0.0594,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50781,0.05637,0.12454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16325.0,"contact_point_centroid":[0.61536,0.17171,0.1314],"force_p95":0.09056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24214,"mean_force":0.05852,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61161,0.19034,0.13049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02621,-0.00207],"force_p95":0.14339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1988,"mean_force":0.1282,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44789,-0.02551,0.03986]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.62784,0.22302,0.11225],"force_p95":0.09724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14778,"mean_force":0.06478,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62208,0.20426,0.11225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":991.0,"contact_point_centroid":[0.62623,0.18542,0.11192],"force_p95":0.09222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14297,"mean_force":0.05635,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62199,0.20423,0.1121]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47787,-0.01202,0.19725]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45484,-0.02502,0.07075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.44682,-0.00625,0.04116],"force_p95":0.06875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10469,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02547,0.03883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5179.0,"contact_point_centroid":[0.44667,-0.0447,0.04066],"force_p95":0.06756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07139,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44682,-0.02547,0.03884]}],"total_contact_groups":13},"final_pose_error":0.01028,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61021,0.19461,0.02683],"final_tcp_position":[0.62405,0.20489,0.11607],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":284.11534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45737,-0.02441,0.09525],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":708.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45426,-0.02574,0.04604],"tcp_start":[0.45737,-0.02441,0.09525],"tcp_to_object_dist_end":0.02049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02564,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14046,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11803.0,"raw_peak_contact_force":0.1988,"subtask_id":"grasp_1","tcp_end":[0.44679,-0.02547,0.03881],"tcp_start":[0.45426,-0.02574,0.04604],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6102,0.1755,0.13155],"object_pos_start":[0.45848,-0.02564,0.02574],"object_to_goal_dist_end":0.04209,"object_to_goal_dist_start":0.30326,"object_z_max":0.14342,"peak_contact_force":284.11534,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35490.0,"raw_peak_contact_force":0.45879,"subtask_id":"transport_arc","tcp_end":[0.60181,0.17553,0.15375],"tcp_start":[0.44679,-0.02547,0.03881],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63025,0.20448,0.08809],"object_pos_start":[0.6102,0.1755,0.13155],"object_to_goal_dist_end":0.0263,"object_to_goal_dist_start":0.04209,"object_z_max":0.13155,"peak_contact_force":0.09833,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30219.0,"raw_peak_contact_force":0.33185,"tcp_end":[0.62405,0.20489,0.11607],"tcp_start":[0.60181,0.17553,0.15375],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61021,0.19461,0.02683],"object_pos_start":[0.63025,0.20448,0.08809],"object_to_goal_dist_end":0.09056,"object_to_goal_dist_start":0.0263,"object_z_max":0.08809,"peak_contact_force":0.20568,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2003.0,"raw_peak_contact_force":1.07451,"subtask_id":"release_1","tcp_end":[0.61724,0.20248,0.13526],"tcp_start":[0.62405,0.20489,0.11607],"tcp_to_object_dist_end":0.10895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11163,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05622,"approach.speed":0.06674,"descend.grasp_z_offset":0.01725,"descend.speed":0.06008,"place_descend.place_height_offset":0.01585,"place_descend.place_speed":0.03459,"transport.arc_height":0.15644,"transport.placement_z_offset":0.01083,"transport.transport_speed":0.01911},"optimized_scores":{"best_composite_score":0.0586,"best_fitness_score":0.6286,"best_task_score":0.32265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.62643,0.13916,-0.01092],"force_p95":1.37536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42311,"mean_force":0.64379,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62527,0.13902,0.21326]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.53888,-0.00024,-0.0014],"force_p95":0.48824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53792,"mean_force":0.22343,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52773,0.00024,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17720.0,"contact_point_centroid":[0.54532,0.04351,0.15546],"force_p95":0.08541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32697,"mean_force":0.05818,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5438,0.02444,0.15333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18423.0,"contact_point_centroid":[0.54508,0.00522,0.15806],"force_p95":0.08106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32519,"mean_force":0.056,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54362,0.02422,0.15629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14999.0,"contact_point_centroid":[0.62577,0.11051,0.20679],"force_p95":0.08952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26265,"mean_force":0.06389,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62151,0.12928,0.20604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14432.0,"contact_point_centroid":[0.62627,0.14824,0.20699],"force_p95":0.08919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21572,"mean_force":0.06619,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62159,0.12938,0.20601]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15356,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53063,0.00088,0.04227]},{"body_a":"world","body_b":"grasp_target","contact_count":2860.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51732,0.00049,0.19549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53057,-0.01834,0.04351],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12301,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52941,0.00086,0.04084]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53658,0.00099,0.07191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":771.0,"contact_point_centroid":[0.63432,0.12123,0.1984],"force_p95":0.0951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10765,"mean_force":0.06444,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62888,0.14004,0.19865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":826.0,"contact_point_centroid":[0.6341,0.1588,0.19842],"force_p95":0.0904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10525,"mean_force":0.0606,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62889,0.14005,0.19868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.5305,0.01994,0.04264],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09406,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52941,0.00086,0.04084]}],"total_contact_groups":13},"final_pose_error":0.02508,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63246,0.13872,0.02322],"final_tcp_position":[0.63044,0.14039,0.2024],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":28.01785,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53722,0.001,0.09307],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":28.01785,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":572.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53784,0.00102,0.05089],"tcp_start":[0.53722,0.001,0.09307],"tcp_to_object_dist_end":0.02569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00076,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13064,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15356,"subtask_id":"grasp_1","tcp_end":[0.52938,0.00086,0.0408],"tcp_start":[0.53784,0.00102,0.05089],"tcp_to_object_dist_end":0.02104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6231,0.11677,0.19439],"object_pos_start":[0.54421,0.00076,0.02587],"object_to_goal_dist_end":0.04815,"object_to_goal_dist_start":0.25049,"object_z_max":0.19935,"peak_contact_force":0.08931,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36228.0,"raw_peak_contact_force":0.53792,"subtask_id":"transport_arc","tcp_end":[0.61424,0.11687,0.21784],"tcp_start":[0.52938,0.00086,0.0408],"tcp_to_object_dist_end":0.02507,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63613,0.14028,0.17317],"object_pos_start":[0.6231,0.11677,0.19439],"object_to_goal_dist_end":0.02777,"object_to_goal_dist_start":0.04815,"object_z_max":0.19439,"peak_contact_force":0.09442,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29431.0,"raw_peak_contact_force":0.26265,"tcp_end":[0.63044,0.14039,0.2024],"tcp_start":[0.61424,0.11687,0.21784],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63246,0.13872,0.02322],"object_pos_start":[0.63613,0.14028,0.17317],"object_to_goal_dist_end":0.16968,"object_to_goal_dist_start":0.02777,"object_z_max":0.17317,"peak_contact_force":0.12815,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1711.0,"raw_peak_contact_force":1.42311,"subtask_id":"release_1","tcp_end":[0.62523,0.13901,0.22187],"tcp_start":[0.63044,0.14039,0.2024],"tcp_to_object_dist_end":0.19879,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```