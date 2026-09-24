## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0199 | 0.29 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3980 | 0.29 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0208 | 0.30 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3194 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.020) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_at_goal
  weight: 0.3
phases:
- id: approach_1
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
    - 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: descend_1
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
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
- id: lift_1
  type: lift
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
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
  subtask_id: transport_to_goal
- id: descend_to_place_1
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
    - 0.02
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.020
- **task_score** (E): 0.290
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1399 |
| descend_1 | 1.00 | 1.00 | 0.1238 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.67 | 1.00 | 0.1386 |
| transport_1 | 0.00 | 1.00 | 0.0795 |
| descend_to_place_1 | 0.67 | 1.00 | 0.1188 |
| release_1 | 1.00 | 1.00 | 0.0223 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.166) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.166)→(0.494, 0.024, 0.043) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.043)→(0.486, 0.023, 0.033) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 42.333 | 0.151 | 0.202 |
| lift_1 | lift | 0.67 / step_budget | (0.486, 0.023, 0.033)→(0.492, 0.023, 0.172) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.156) | 0.272→0.215 | 1.00 / 37.000 | 0.082 | 0.569 |
| transport_1 | approach | 0.00 / step_budget | (0.492, 0.023, 0.172)→(0.519, 0.070, 0.229) | (0.501, 0.024, 0.156)→(0.524, 0.072, 0.208) | 0.215→0.159 | 1.00 / 32.667 | 0.088 | 0.125 |
| descend_to_place_1 | descend | 0.67 / step_budget | (0.519, 0.070, 0.229)→(0.577, 0.161, 0.210) | (0.524, 0.072, 0.208)→(0.578, 0.162, 0.184) | 0.159→0.049 | 1.00 / 33.333 | 0.084 | 0.142 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.161, 0.210)→(0.572, 0.159, 0.232) | (0.578, 0.162, 0.184)→(0.571, 0.159, 0.019) | 0.049→0.195 | 1.00 / 2.667 | 0.189 | 1.510 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.444
- phase_score: 0.350
- phase_breakdown.approach_object_score: 0.166
- phase_breakdown.transport_to_goal_score: 0.057
- phase_breakdown.lift_object_score: 0.771
- phase_breakdown.place_at_goal_score: 0.484
- grasp_place_fitness: 0.698

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.698
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.444
- **Median Q (composite search score)**: -0.012
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.357


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23445,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04695,"approach_1.approach_z_offset":0.07268,"descend_1.descend_speed":0.07495,"descend_1.descend_z_offset":0.00958,"descend_to_place_1.place_speed":0.07453,"lift_1.lift_height":0.14158,"lift_1.lift_speed":0.06068,"transport_1.transport_height":0.10016,"transport_1.transport_speed":0.05498},"optimized_scores":{"best_composite_score":-0.02663,"best_fitness_score":0.57337,"best_task_score":0.19902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.54701,0.11663,-0.01257],"force_p95":1.53402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6049,"mean_force":0.76745,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5475,0.11888,0.23959]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.50001,-0.01536,-0.0011],"force_p95":0.32101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47949,"mean_force":0.08469,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48833,-0.01536,0.03631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20733.0,"contact_point_centroid":[0.49215,0.00354,0.08453],"force_p95":0.07321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25806,"mean_force":0.04913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49092,-0.01548,0.08271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18045.0,"contact_point_centroid":[0.49139,-0.03466,0.08553],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25613,"mean_force":0.05515,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49092,-0.01548,0.08283]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16132,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01538,0.03603]},{"body_a":"world","body_b":"grasp_target","contact_count":2512.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49851,-0.00712,0.20559]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49754,-0.01495,0.07736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":997.0,"contact_point_centroid":[0.55023,0.139,0.22321],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.121,"mean_force":0.05093,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55077,0.1197,0.2216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17795.0,"contact_point_centroid":[0.50778,-0.00542,0.16141],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11962,"mean_force":0.05463,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50586,0.0136,0.15956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1069.0,"contact_point_centroid":[0.55714,0.10153,0.22153],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11758,"mean_force":0.04806,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55077,0.1197,0.2216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18315.0,"contact_point_centroid":[0.50701,0.03304,0.16169],"force_p95":0.07721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10801,"mean_force":0.05268,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50603,0.014,0.15995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16886.0,"contact_point_centroid":[0.5352,0.10217,0.20657],"force_p95":0.07856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10473,"mean_force":0.05636,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53476,0.083,0.2047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17448.0,"contact_point_centroid":[0.54083,0.06605,0.2065],"force_p95":0.08604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10392,"mean_force":0.055,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53545,0.08449,0.20548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.49057,0.00369,0.03674],"force_p95":0.06668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09624,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48971,-0.01536,0.03474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.48928,-0.03464,0.03742],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09413,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48971,-0.01536,0.03474]}],"total_contact_groups":15},"final_pose_error":0.0877,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55403,0.12067,0.01769],"final_tcp_position":[0.55217,0.11986,0.22436],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.6049,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2512.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.4993,-0.01451,0.11131],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49822,-0.01543,0.04387],"tcp_start":[0.4993,-0.01451,0.11131],"tcp_to_object_dist_end":0.01871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01576,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31243,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13308,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11274.0,"raw_peak_contact_force":0.16132,"subtask_id":"lift_object","tcp_end":[0.48968,-0.01536,0.0347],"tcp_start":[0.49822,-0.01543,0.04387],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50509,-0.01596,0.11794],"object_pos_start":[0.50369,-0.01576,0.02588],"object_to_goal_dist_end":0.25498,"object_to_goal_dist_start":0.31243,"object_z_max":0.11782,"peak_contact_force":0.08195,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38951.0,"raw_peak_contact_force":0.47949,"subtask_id":"lift_object","tcp_end":[0.49654,-0.01563,0.13406],"tcp_start":[0.48968,-0.01536,0.0347],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52285,0.04026,0.16535],"object_pos_start":[0.50509,-0.01596,0.11794],"object_to_goal_dist_end":0.1806,"object_to_goal_dist_start":0.25498,"object_z_max":0.16529,"peak_contact_force":0.08793,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36110.0,"raw_peak_contact_force":0.11962,"subtask_id":"transport_to_goal","tcp_end":[0.51759,0.0398,0.18678],"tcp_start":[0.49654,-0.01563,0.13406],"tcp_to_object_dist_end":0.02207,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55726,0.12175,0.19879],"object_pos_start":[0.52285,0.04026,0.16535],"object_to_goal_dist_end":0.08734,"object_to_goal_dist_start":0.1806,"object_z_max":0.19876,"peak_contact_force":0.0804,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34334.0,"raw_peak_contact_force":0.10473,"subtask_id":"place_at_goal","tcp_end":[0.55217,0.11986,0.22436],"tcp_start":[0.51759,0.0398,0.18678],"tcp_to_object_dist_end":0.02613,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55403,0.12067,0.01769],"object_pos_start":[0.55726,0.12175,0.19879],"object_to_goal_dist_end":0.24215,"object_to_goal_dist_start":0.08734,"object_z_max":0.19879,"peak_contact_force":0.19289,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2165.0,"raw_peak_contact_force":1.6049,"subtask_id":"place_at_goal","tcp_end":[0.54745,0.11888,0.24719],"tcp_start":[0.55217,0.11986,0.22436],"tcp_to_object_dist_end":0.2296,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27232,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.051,"approach_1.approach_z_offset":0.18682,"descend_1.descend_speed":0.05289,"descend_1.descend_z_offset":0.00594,"descend_to_place_1.place_speed":0.08595,"lift_1.lift_height":0.26236,"lift_1.lift_speed":0.09866,"transport_1.transport_height":0.21417,"transport_1.transport_speed":0.02803},"optimized_scores":{"best_composite_score":0.09836,"best_fitness_score":0.69836,"best_task_score":0.444},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":279.0,"contact_point_centroid":[0.60078,0.16446,-0.00502],"force_p95":0.83076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23256,"mean_force":0.24909,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61511,0.16725,0.16826]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.50914,0.03731,-0.00123],"force_p95":0.43236,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65611,"mean_force":0.09239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49718,0.03807,0.03281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49934,0.05726,0.11178],"force_p95":0.08316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34034,"mean_force":0.05885,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.499,0.03806,0.10902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20614.0,"contact_point_centroid":[0.50091,0.01914,0.10911],"force_p95":0.0787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31463,"mean_force":0.04996,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49891,0.03806,0.10753]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03966,-0.00214],"force_p95":0.16136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2222,"mean_force":0.13275,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49987,0.03831,0.03228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":939.0,"contact_point_centroid":[0.61459,0.18703,0.15497],"force_p95":0.09081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21914,"mean_force":0.0552,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61927,0.1685,0.15484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1058.0,"contact_point_centroid":[0.62267,0.14997,0.15214],"force_p95":0.08001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19893,"mean_force":0.05071,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61928,0.1685,0.15485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19676.0,"contact_point_centroid":[0.58611,0.10954,0.19053],"force_p95":0.0765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19251,"mean_force":0.04912,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58278,0.12834,0.19006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17128.0,"contact_point_centroid":[0.58058,0.14811,0.19205],"force_p95":0.08738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18891,"mean_force":0.05453,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58373,0.12935,0.18924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5024.0,"contact_point_centroid":[0.50029,0.0192,0.03243],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17618,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49863,0.03821,0.03093]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50266,0.01621,0.26151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15741.0,"contact_point_centroid":[0.5205,0.07877,0.21334],"force_p95":0.08889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12733,"mean_force":0.06145,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52059,0.05965,0.21121]},{"body_a":"world","body_b":"grasp_target","contact_count":2440.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50601,0.03625,0.13077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18558.0,"contact_point_centroid":[0.524,0.04102,0.21198],"force_p95":0.08014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11407,"mean_force":0.05276,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52057,0.05962,0.21118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4228.0,"contact_point_centroid":[0.49892,0.05752,0.03367],"force_p95":0.08314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09235,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49864,0.03821,0.03094]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6012,0.16446,0.0264],"final_tcp_position":[0.62103,0.16888,0.15841],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.23256,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50749,0.03382,0.223],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2440.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50724,0.0389,0.04036],"tcp_start":[0.50749,0.03382,0.223],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.0388,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21308,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15867,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.2222,"subtask_id":"lift_object","tcp_end":[0.4986,0.0382,0.0309],"tcp_start":[0.50724,0.0389,0.04036],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51379,0.03912,0.17582],"object_pos_start":[0.51249,0.0388,0.02553],"object_to_goal_dist_end":0.17801,"object_to_goal_dist_start":0.21308,"object_z_max":0.17564,"peak_contact_force":0.0813,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37760.0,"raw_peak_contact_force":0.65611,"subtask_id":"lift_object","tcp_end":[0.50382,0.03829,0.18957],"tcp_start":[0.4986,0.0382,0.0309],"tcp_to_object_dist_end":0.017,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5444,0.07997,0.21483],"object_pos_start":[0.51379,0.03912,0.17582],"object_to_goal_dist_end":0.14267,"object_to_goal_dist_start":0.17801,"object_z_max":0.21479,"peak_contact_force":0.08769,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34299.0,"raw_peak_contact_force":0.12733,"subtask_id":"transport_to_goal","tcp_end":[0.53821,0.07866,0.23464],"tcp_start":[0.50382,0.03829,0.18957],"tcp_to_object_dist_end":0.0208,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.61357,0.16901,0.13109],"object_pos_start":[0.5444,0.07997,0.21483],"object_to_goal_dist_end":0.02006,"object_to_goal_dist_start":0.14267,"object_z_max":0.21483,"peak_contact_force":0.09229,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36804.0,"raw_peak_contact_force":0.19251,"subtask_id":"place_at_goal","tcp_end":[0.62103,0.16888,0.15841],"tcp_start":[0.53821,0.07866,0.23464],"tcp_to_object_dist_end":0.02832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6012,0.16446,0.0264],"object_pos_start":[0.61357,0.16901,0.13109],"object_to_goal_dist_end":0.12179,"object_to_goal_dist_start":0.02006,"object_z_max":0.13109,"peak_contact_force":0.11722,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2276.0,"raw_peak_contact_force":1.23256,"subtask_id":"place_at_goal","tcp_end":[0.61503,0.16723,0.17864],"tcp_start":[0.62103,0.16888,0.15841],"tcp_to_object_dist_end":0.1529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16735,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04166,"approach_1.approach_z_offset":0.12642,"descend_1.descend_speed":0.05674,"descend_1.descend_z_offset":0.00891,"descend_to_place_1.place_speed":0.0477,"lift_1.lift_height":0.21562,"lift_1.lift_speed":0.09815,"transport_1.transport_height":0.27445,"transport_1.transport_speed":0.02148},"optimized_scores":{"best_composite_score":-0.01196,"best_fitness_score":0.58804,"best_task_score":0.22753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.55419,0.18989,-0.0138],"force_p95":1.64158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69293,"mean_force":0.90609,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5538,0.19164,0.26238]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.47956,0.04613,-0.00123],"force_p95":0.35268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5711,"mean_force":0.08209,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46812,0.0468,0.03682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47063,0.06607,0.11524],"force_p95":0.08453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32456,"mean_force":0.05865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47077,0.04687,0.11253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20879.0,"contact_point_centroid":[0.4728,0.02797,0.11299],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29708,"mean_force":0.04916,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4707,0.04687,0.11144]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":905.0,"contact_point_centroid":[0.55385,0.21173,0.24552],"force_p95":0.08671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23247,"mean_force":0.05762,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55668,0.19278,0.24397]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04867,-0.00215],"force_p95":0.16475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22267,"mean_force":0.13385,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47065,0.04707,0.03608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1014.0,"contact_point_centroid":[0.56452,0.17535,0.24284],"force_p95":0.08201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21025,"mean_force":0.05235,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55667,0.19278,0.24394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.47128,0.02796,0.03614],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19804,"mean_force":0.04265,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46945,0.04695,0.03487]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4895,0.02124,0.23249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18588.0,"contact_point_centroid":[0.53662,0.12815,0.25399],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12972,"mean_force":0.05336,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.52981,0.14605,0.25333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16898.0,"contact_point_centroid":[0.48637,0.09034,0.23173],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12953,"mean_force":0.05689,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48749,0.07123,0.22896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17134.0,"contact_point_centroid":[0.52815,0.16527,0.25594],"force_p95":0.07966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12525,"mean_force":0.05643,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.52991,0.14622,0.2533]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47777,0.04565,0.10346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19794.0,"contact_point_centroid":[0.49098,0.05247,0.23017],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11601,"mean_force":0.04926,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48745,0.07117,0.22886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4233.0,"contact_point_centroid":[0.46934,0.06628,0.03733],"force_p95":0.08711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09423,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46946,0.04696,0.03487]}],"total_contact_groups":15},"final_pose_error":0.04313,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55629,0.1916,0.01306],"final_tcp_position":[0.558,0.19309,0.24701],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.69293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48062,0.04383,0.16465],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47774,0.04776,0.0434],"tcp_start":[0.48062,0.04383,0.16465],"tcp_to_object_dist_end":0.0181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48273,0.04773,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29097,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16152,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11114.0,"raw_peak_contact_force":0.22267,"subtask_id":"lift_object","tcp_end":[0.46943,0.04695,0.03484],"tcp_start":[0.47774,0.04776,0.0434],"tcp_to_object_dist_end":0.01629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48527,0.04814,0.17561],"object_pos_start":[0.48273,0.04773,0.02548],"object_to_goal_dist_end":0.21213,"object_to_goal_dist_start":0.29097,"object_z_max":0.17543,"peak_contact_force":0.08165,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38022.0,"raw_peak_contact_force":0.5711,"subtask_id":"lift_object","tcp_end":[0.47635,0.04721,0.19221],"tcp_start":[0.46943,0.04695,0.03484],"tcp_to_object_dist_end":0.01887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.09431,0.24415],"object_pos_start":[0.48527,0.04814,0.17561],"object_to_goal_dist_end":0.15514,"object_to_goal_dist_start":0.21213,"object_z_max":0.24407,"peak_contact_force":0.0892,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36692.0,"raw_peak_contact_force":0.12953,"subtask_id":"transport_to_goal","tcp_end":[0.50023,0.0928,0.26566],"tcp_start":[0.47635,0.04721,0.19221],"tcp_to_object_dist_end":0.02228,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56268,0.19599,0.22135],"object_pos_start":[0.50585,0.09431,0.24415],"object_to_goal_dist_end":0.03914,"object_to_goal_dist_start":0.15514,"object_z_max":0.24417,"peak_contact_force":0.07982,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":35722.0,"raw_peak_contact_force":0.12972,"subtask_id":"place_at_goal","tcp_end":[0.558,0.19309,0.24701],"tcp_start":[0.50023,0.0928,0.26566],"tcp_to_object_dist_end":0.02625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55629,0.1916,0.01306],"object_pos_start":[0.56268,0.19599,0.22135],"object_to_goal_dist_end":0.22207,"object_to_goal_dist_start":0.03914,"object_z_max":0.22135,"peak_contact_force":0.2558,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2005.0,"raw_peak_contact_force":1.69293,"subtask_id":"place_at_goal","tcp_end":[0.55376,0.19163,0.26902],"tcp_start":[0.558,0.19309,0.24701],"tcp_to_object_dist_end":0.25597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```