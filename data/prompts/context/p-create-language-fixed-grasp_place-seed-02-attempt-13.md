## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1683 | 0.38 | ❌ rejected |
| 12 | approach → descend → grasp → approach → descend → retract → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2507 | 0.23 | ❌ rejected |
| 11 | approach → descend → grasp → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1207 | 0.40 | ❌ rejected |
| 10 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0919 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3153 | 0.77 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.168) — your mutation base

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

- **Composite score**: -0.168
- **task_score** (E): 0.384
- **fitness_score**: 0.582  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2118 |
| descend | 1.00 | 1.00 | 0.0480 |
| grasp | 1.00 | 1.00 | 0.0115 |
| lift | 0.67 | 1.00 | 0.0801 |
| transport | 1.00 | 1.00 | 0.2500 |
| place_descend | 1.00 | 1.00 | 0.0212 |
| release | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.093) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 7.660 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.490, -0.014, 0.093)→(0.488, -0.015, 0.045) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.045)→(0.480, -0.015, 0.037) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.135 | 0.176 |
| lift | retract | 0.67 / step_budget | (0.480, -0.015, 0.037)→(0.476, -0.015, 0.117) | (0.493, -0.015, 0.026)→(0.484, -0.015, 0.100) | 0.281→0.261 | 1.00 / 39.000 | 0.076 | 0.504 |
| transport | approach | 1.00 / step_budget | (0.476, -0.015, 0.117)→(0.622, 0.160, 0.197) | (0.484, -0.015, 0.100)→(0.629, 0.160, 0.174) | 0.261→0.023 | 1.00 / 25.667 | 0.102 | 0.150 |
| place_descend | descend | 1.00 / step_budget | (0.622, 0.160, 0.197)→(0.629, 0.171, 0.182) | (0.629, 0.160, 0.174)→(0.637, 0.176, 0.117) | 0.023→0.050 | 1.00 / 15.333 | 0.124 | 0.698 |
| release | release | 1.00 / step_budget | (0.629, 0.171, 0.182)→(0.624, 0.169, 0.201) | (0.637, 0.176, 0.117)→(0.639, 0.176, 0.018) | 0.050→0.148 | 1.00 / 3.333 | 0.148 | 1.135 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.516
- phase_score: 0.483
- phase_breakdown.transport_arc_score: 0.345
- phase_breakdown.approach_1_score: 0.196
- phase_breakdown.release_1_score: 0.305
- phase_breakdown.descend_1_score: 0.873
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.732

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.732
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: -0.115
- **K-run variance**: 0.0222
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90769,"average_solve_count":325.0,"average_success_count":325.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.06001,"approach.speed":0.02604,"descend.grasp_z_offset":0.01096,"descend.speed":0.08351,"lift.lift_height":0.14723,"lift.lift_speed":0.05556,"place_descend.place_speed":0.01013,"place_descend.placement_z_offset":0.02902,"release.release_duration":1.44316,"transport.arc_height":0.06075,"transport.placement_z_offset":0.01356,"transport.transport_speed":0.04306},"optimized_scores":{"best_composite_score":-0.11469,"best_fitness_score":0.63531,"best_task_score":0.32521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.61564,0.15195,-0.01092],"force_p95":1.38361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51097,"mean_force":0.64766,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6146,0.14949,0.21375]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.47196,-0.01937,-0.00117],"force_p95":0.31251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49701,"mean_force":0.08682,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.46215,-0.01952,0.03958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15263.0,"contact_point_centroid":[0.62156,0.16741,0.2011],"force_p95":0.09197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31145,"mean_force":0.06215,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61698,0.14853,0.20022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19941.0,"contact_point_centroid":[0.45979,-0.03858,0.08835],"force_p95":0.07535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2844,"mean_force":0.05099,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.45969,-0.01944,0.08652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19958.0,"contact_point_centroid":[0.45978,-0.00031,0.09022],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28379,"mean_force":0.05064,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.45969,-0.01944,0.08818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14837.0,"contact_point_centroid":[0.62143,0.12969,0.20101],"force_p95":0.0933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26214,"mean_force":0.06375,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61701,0.14855,0.20024]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02006,-0.00205],"force_p95":0.13806,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17942,"mean_force":0.12681,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46482,-0.01958,0.03908]},{"body_a":"world","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48592,-0.00918,0.19948]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47156,-0.01916,0.07257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15492.0,"contact_point_centroid":[0.5217,0.0272,0.19827],"force_p95":0.07959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11442,"mean_force":0.0542,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52008,0.04611,0.19734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13719.0,"contact_point_centroid":[0.5231,0.06645,0.1991],"force_p95":0.08716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11412,"mean_force":0.06037,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52133,0.04739,0.19742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.62385,0.16933,0.19828],"force_p95":0.09537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10564,"mean_force":0.06389,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61816,0.15057,0.19879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46351,-0.0003,0.04089],"force_p95":0.06646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1044,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01955,0.03798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":771.0,"contact_point_centroid":[0.624,0.13185,0.19851],"force_p95":0.09467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09966,"mean_force":0.06405,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61818,0.15057,0.19883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46338,-0.0388,0.04039],"force_p95":0.06526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08515,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01955,0.03799]}],"total_contact_groups":15},"final_pose_error":0.02188,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62339,0.14686,0.02217],"final_tcp_position":[0.61972,0.15098,0.20247],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":22.73438,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":22.73438,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47375,-0.01866,0.09949],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47139,-0.01973,0.04573],"tcp_start":[0.47375,-0.01866,0.09949],"tcp_to_object_dist_end":0.02029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01966,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1361,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.17942,"subtask_id":"grasp_1","tcp_end":[0.46369,-0.01955,0.03796],"tcp_start":[0.47139,-0.01973,0.04573],"tcp_to_object_dist_end":0.01734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46624,-0.0196,0.11577],"object_pos_start":[0.47607,-0.01966,0.0258],"object_to_goal_dist_end":0.25449,"object_to_goal_dist_start":0.28825,"object_z_max":0.11566,"peak_contact_force":0.07772,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":40063.0,"raw_peak_contact_force":0.49701,"tcp_end":[0.45966,-0.01943,0.13497],"tcp_start":[0.46369,-0.01955,0.03796],"tcp_to_object_dist_end":0.0203,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.62272,0.14602,0.18077],"object_pos_start":[0.46624,-0.0196,0.11577],"object_to_goal_dist_end":0.0183,"object_to_goal_dist_start":0.25449,"object_z_max":0.20345,"peak_contact_force":0.09055,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29211.0,"raw_peak_contact_force":0.11442,"subtask_id":"transport_arc","tcp_end":[0.61662,0.14603,0.20484],"tcp_start":[0.45966,-0.01943,0.13497],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62541,0.15103,0.17295],"object_pos_start":[0.62272,0.14602,0.18077],"object_to_goal_dist_end":0.01985,"object_to_goal_dist_start":0.0183,"object_z_max":0.18077,"peak_contact_force":0.09507,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30100.0,"raw_peak_contact_force":0.31145,"tcp_end":[0.61972,0.15098,0.20247],"tcp_start":[0.61662,0.14603,0.20484],"tcp_to_object_dist_end":0.03006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62339,0.14686,0.02217],"object_pos_start":[0.62541,0.15103,0.17295],"object_to_goal_dist_end":0.16849,"object_to_goal_dist_start":0.01985,"object_z_max":0.17295,"peak_contact_force":0.21715,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1665.0,"raw_peak_contact_force":1.51097,"subtask_id":"release_1","tcp_end":[0.61456,0.14948,0.2223],"tcp_start":[0.61972,0.15098,0.20247],"tcp_to_object_dist_end":0.20034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15663,"average_solve_count":332.0,"average_success_count":332.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.07187,"approach.speed":0.03216,"descend.grasp_z_offset":0.01002,"descend.speed":0.07547,"lift.lift_height":0.12643,"lift.lift_speed":0.04273,"place_descend.place_speed":0.04329,"place_descend.placement_z_offset":0.04813,"release.release_duration":1.10774,"transport.arc_height":0.11115,"transport.placement_z_offset":0.02163,"transport.transport_speed":0.04604},"optimized_scores":{"best_composite_score":-0.01849,"best_fitness_score":0.73151,"best_task_score":0.51573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.63805,0.2212,-0.00237],"force_p95":0.16573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46892,"mean_force":0.14551,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6219,0.20247,0.15349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2433.0,"contact_point_centroid":[0.62038,0.17741,0.15321],"force_p95":0.17649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56616,"mean_force":0.12182,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61544,0.19564,0.15526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3103.0,"contact_point_centroid":[0.621,0.21359,0.15308],"force_p95":0.13672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50001,"mean_force":0.09519,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6155,0.19569,0.15526]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.45407,-0.02504,-0.00119],"force_p95":0.4176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47956,"mean_force":0.10411,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.44525,-0.02548,0.0391]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21088.0,"contact_point_centroid":[0.44255,-0.04449,0.09052],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26635,"mean_force":0.04845,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.44278,-0.02537,0.0887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19889.0,"contact_point_centroid":[0.44266,-0.00618,0.08982],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26061,"mean_force":0.05064,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.44279,-0.02537,0.08766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15687.0,"contact_point_centroid":[0.50987,0.03894,0.20805],"force_p95":0.09747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20982,"mean_force":0.06306,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50688,0.05763,0.20713]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02621,-0.00207],"force_p95":0.14225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1934,"mean_force":0.12785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44777,-0.02557,0.03863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13532.0,"contact_point_centroid":[0.51102,0.07793,0.20738],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19071,"mean_force":0.07193,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50799,0.05902,0.20584]},{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47809,-0.01189,0.20567]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45489,-0.02498,0.07804]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63816,0.22154,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62101,0.20443,0.15307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.44672,-0.00631,0.03999],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10276,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4467,-0.02553,0.03761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44658,-0.04476,0.03949],"force_p95":0.06744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07331,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4467,-0.02553,0.03762]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2060.0,"contact_point_centroid":[0.62274,0.20285,0.1557],"force_p95":0.01157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01066,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62226,0.20284,0.15345]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62415,0.20554,0.15195],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62389,0.20552,0.14998]}],"total_contact_groups":16},"final_pose_error":0.01056,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63816,0.22154,0.01602],"final_tcp_position":[0.62532,0.206,0.15312],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.46892,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45765,-0.02428,0.1114],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45419,-0.0258,0.04484],"tcp_start":[0.45765,-0.02428,0.1114],"tcp_to_object_dist_end":0.01933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02568,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13946,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11798.0,"raw_peak_contact_force":0.1934,"subtask_id":"grasp_1","tcp_end":[0.44667,-0.02553,0.03759],"tcp_start":[0.45419,-0.0258,0.04484],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44894,-0.02534,0.12217],"object_pos_start":[0.45848,-0.02568,0.02576],"object_to_goal_dist_end":0.29571,"object_to_goal_dist_start":0.30328,"object_z_max":0.12207,"peak_contact_force":0.06993,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":41132.0,"raw_peak_contact_force":0.47956,"tcp_end":[0.44286,-0.02536,0.14029],"tcp_start":[0.44667,-0.02553,0.03759],"tcp_to_object_dist_end":0.01911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62478,0.19328,0.13805],"object_pos_start":[0.44894,-0.02534,0.12217],"object_to_goal_dist_end":0.02871,"object_to_goal_dist_start":0.29571,"object_z_max":0.21976,"peak_contact_force":0.10873,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29219.0,"raw_peak_contact_force":0.20982,"subtask_id":"transport_arc","tcp_end":[0.61599,0.19359,0.16329],"tcp_start":[0.44286,-0.02536,0.14029],"tcp_to_object_dist_end":0.02673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.63816,0.22154,0.01602],"object_pos_start":[0.62478,0.19328,0.13805],"object_to_goal_dist_end":0.09933,"object_to_goal_dist_start":0.02871,"object_z_max":0.13805,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9784.0,"raw_peak_contact_force":1.46892,"tcp_end":[0.62532,0.206,0.15312],"tcp_start":[0.61599,0.19359,0.16329],"tcp_to_object_dist_end":0.13857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63816,0.22154,0.01602],"object_pos_start":[0.63816,0.22154,0.01602],"object_to_goal_dist_end":0.09933,"object_to_goal_dist_start":0.09933,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61932,0.20377,0.17226],"tcp_start":[0.62532,0.206,0.15312],"tcp_to_object_dist_end":0.15838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.03116,"approach.speed":0.01954,"descend.grasp_z_offset":0.0114,"descend.speed":0.04006,"lift.lift_height":0.05013,"lift.lift_speed":0.08501,"place_descend.place_speed":0.03571,"place_descend.placement_z_offset":0.00786,"release.release_duration":1.44318,"transport.arc_height":0.17571,"transport.placement_z_offset":0.03136,"transport.transport_speed":0.03241},"optimized_scores":{"best_composite_score":-0.37167,"best_fitness_score":0.37833,"best_task_score":0.31177},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.65337,0.15885,-0.00566],"force_p95":1.02117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77032,"mean_force":0.28018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63793,0.15483,0.19877]},{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.53846,0.00065,-0.00118],"force_p95":0.38528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53687,"mean_force":0.10598,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.52708,0.00082,0.03611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9548.0,"contact_point_centroid":[0.64142,0.13063,0.20186],"force_p95":0.14724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31459,"mean_force":0.08793,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63695,0.14917,0.20208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10602.0,"contact_point_centroid":[0.64217,0.16749,0.20203],"force_p95":0.12892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31007,"mean_force":0.07977,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63688,0.1491,0.20223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8400.0,"contact_point_centroid":[0.52581,-0.01833,0.05705],"force_p95":0.08123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30993,"mean_force":0.05737,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.5246,0.00078,0.05469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8916.0,"contact_point_centroid":[0.52581,0.01982,0.0559],"force_p95":0.07822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29529,"mean_force":0.05487,"phase_index":3.0,"phase_name":"lift","phase_type":"retract","tcp_position_centroid":[0.52464,0.00078,0.05389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":299.0,"contact_point_centroid":[0.6466,0.13816,0.18239],"force_p95":0.20279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21198,"mean_force":0.14419,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64199,0.15606,0.18722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":443.0,"contact_point_centroid":[0.6472,0.17349,0.18256],"force_p95":0.13863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15583,"mean_force":0.09309,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64186,0.15603,0.18692]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15581,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53025,0.00087,0.03604]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51732,0.00049,0.18273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17503.0,"contact_point_centroid":[0.55166,0.01824,0.18053],"force_p95":0.08165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12563,"mean_force":0.05686,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54977,0.03714,0.17939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16035.0,"contact_point_centroid":[0.55327,0.05805,0.18082],"force_p95":0.08759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12414,"mean_force":0.0613,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5513,0.03902,0.17908]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53678,0.00099,0.05659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53032,-0.01835,0.03728],"force_p95":0.07623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11996,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52902,0.00085,0.03461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53022,0.01993,0.0364],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09019,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52902,0.00085,0.03462]}],"total_contact_groups":15},"final_pose_error":0.00969,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65477,0.15836,0.01643],"final_tcp_position":[0.6433,0.1564,0.19046],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.77032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53727,0.001,0.06805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53753,0.00101,0.04463],"tcp_start":[0.53727,0.001,0.06805],"tcp_to_object_dist_end":0.0198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13052,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15581,"subtask_id":"grasp_1","tcp_end":[0.52899,0.00085,0.03458],"tcp_start":[0.53753,0.00101,0.04463],"tcp_to_object_dist_end":0.01752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.53636,0.00079,0.06141],"object_pos_start":[0.54419,0.00074,0.02587],"object_to_goal_dist_end":0.23226,"object_to_goal_dist_start":0.25051,"object_z_max":0.06135,"peak_contact_force":0.08129,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":17515.0,"raw_peak_contact_force":0.53687,"tcp_end":[0.5243,0.00078,0.07479],"tcp_start":[0.52899,0.00085,0.03458],"tcp_to_object_dist_end":0.01801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64022,0.14072,0.20285],"object_pos_start":[0.53636,0.00079,0.06141],"object_to_goal_dist_end":0.02223,"object_to_goal_dist_start":0.23226,"object_z_max":0.21626,"peak_contact_force":0.10811,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33538.0,"raw_peak_contact_force":0.12563,"subtask_id":"transport_arc","tcp_end":[0.63214,0.14099,0.22407],"tcp_start":[0.5243,0.00078,0.07479],"tcp_to_object_dist_end":0.02272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.64757,0.15648,0.16137],"object_pos_start":[0.64022,0.14072,0.20285],"object_to_goal_dist_end":0.02977,"object_to_goal_dist_start":0.02223,"object_z_max":0.20285,"peak_contact_force":0.15413,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20150.0,"raw_peak_contact_force":0.31459,"tcp_end":[0.6433,0.1564,0.19046],"tcp_start":[0.63214,0.14099,0.22407],"tcp_to_object_dist_end":0.0294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65477,0.15836,0.01643],"object_pos_start":[0.64757,0.15648,0.16137],"object_to_goal_dist_end":0.17482,"object_to_goal_dist_start":0.02977,"object_z_max":0.16137,"peak_contact_force":0.10364,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":1.77032,"subtask_id":"release_1","tcp_end":[0.63788,0.15482,0.20924],"tcp_start":[0.6433,0.1564,0.19046],"tcp_to_object_dist_end":0.19359,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```