## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0208 | 0.30 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3194 | 0.17 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.021) — your mutation base

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

- **Composite score**: 0.021
- **task_score** (E): 0.296
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1378 |
| descend_1 | 1.00 | 1.00 | 0.1235 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.33 | 1.00 | 0.1479 |
| transport_1 | 0.00 | 1.00 | 0.0853 |
| descend_to_place_1 | 0.33 | 0.67 | 0.1201 |
| release_1 | 1.00 | 1.00 | 0.0222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.168) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.168)→(0.494, 0.024, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 17.749 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.024, 0.045)→(0.486, 0.023, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.667 | 0.152 | 0.205 |
| lift_1 | lift | 0.33 / step_budget | (0.486, 0.023, 0.036)→(0.493, 0.023, 0.183) | (0.500, 0.024, 0.026)→(0.502, 0.024, 0.166) | 0.272→0.208 | 1.00 / 37.333 | 0.080 | 0.573 |
| transport_1 | approach | 0.00 / step_budget | (0.493, 0.023, 0.183)→(0.521, 0.072, 0.247) | (0.502, 0.024, 0.166)→(0.526, 0.073, 0.224) | 0.208→0.152 | 1.00 / 32.333 | 0.092 | 0.132 |
| descend_to_place_1 | descend | 0.33 / step_budget | (0.521, 0.072, 0.247)→(0.579, 0.166, 0.220) | (0.526, 0.073, 0.224)→(0.583, 0.159, 0.164) | 0.152→0.063 | 0.67 / 25.667 | 0.050 | 0.240 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.166, 0.220)→(0.575, 0.164, 0.241) | (0.583, 0.159, 0.164)→(0.579, 0.160, 0.021) | 0.063→0.192 | 1.00 / 3.000 | 0.342 | 1.789 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.452
- phase_score: 0.369
- phase_breakdown.approach_object_score: 0.170
- phase_breakdown.transport_to_goal_score: 0.069
- phase_breakdown.lift_object_score: 0.853
- phase_breakdown.place_at_goal_score: 0.480
- grasp_place_fitness: 0.701

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.452
- **Median Q (composite search score)**: -0.010
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: lift_1.lift_height
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16996,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09452,"approach_1.approach_z_offset":0.11794,"descend_1.descend_speed":0.03727,"descend_1.descend_z_offset":0.01804,"descend_to_place_1.place_speed":0.01701,"lift_1.lift_height":0.29999,"lift_1.lift_speed":0.09982,"transport_1.transport_height":0.27891,"transport_1.transport_speed":0.06264},"optimized_scores":{"best_composite_score":-0.02869,"best_fitness_score":0.57131,"best_task_score":0.2109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.56701,0.11298,-0.00496],"force_p95":1.01683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17602,"mean_force":0.26612,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55865,0.13939,0.26802]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.50091,-0.01519,-0.00111],"force_p95":0.30832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48178,"mean_force":0.07191,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48883,-0.01538,0.04494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10323.0,"contact_point_centroid":[0.53433,0.10146,0.26632],"force_p95":0.13729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36998,"mean_force":0.08413,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53503,0.08277,0.2691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21399.0,"contact_point_centroid":[0.49126,0.00368,0.12125],"force_p95":0.07317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30432,"mean_force":0.04856,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49006,-0.01543,0.11922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19633.0,"contact_point_centroid":[0.49074,-0.03463,0.12483],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29487,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49021,-0.01543,0.1218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11112.0,"contact_point_centroid":[0.54098,0.06782,0.26569],"force_p95":0.11293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19928,"mean_force":0.07847,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53636,0.08561,0.26883]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01575,-0.00203],"force_p95":0.13461,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16378,"mean_force":0.12568,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49138,-0.0154,0.04452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18608.0,"contact_point_centroid":[0.50517,-0.00853,0.24251],"force_p95":0.07396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15207,"mean_force":0.05221,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50359,0.01049,0.24151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18709.0,"contact_point_centroid":[0.50407,0.02968,0.24218],"force_p95":0.07504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14496,"mean_force":0.0524,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50365,0.01061,0.2417]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4988,-0.00687,0.22872]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49766,-0.01478,0.10418]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5778.0,"contact_point_centroid":[0.49057,0.00386,0.04598],"force_p95":0.06305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08961,"mean_force":0.03851,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49017,-0.01538,0.04322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5120.0,"contact_point_centroid":[0.48981,-0.03466,0.0474],"force_p95":0.06761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08095,"mean_force":0.04276,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49017,-0.01538,0.04322]}],"total_contact_groups":13},"final_pose_error":0.05356,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56312,0.12037,0.02578],"final_tcp_position":[0.56205,0.14017,0.26413],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.17602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.49963,-0.01417,0.15665],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49855,-0.01545,0.05236],"tcp_start":[0.49963,-0.01417,0.15665],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01569,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31239,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13486,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12698.0,"raw_peak_contact_force":0.16378,"subtask_id":"lift_object","tcp_end":[0.49014,-0.01538,0.04318],"tcp_start":[0.49855,-0.01545,0.05236],"tcp_to_object_dist_end":0.02203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5026,-0.01593,0.18169],"object_pos_start":[0.50373,-0.01569,0.02585],"object_to_goal_dist_end":0.22996,"object_to_goal_dist_start":0.31239,"object_z_max":0.1815,"peak_contact_force":0.07898,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41165.0,"raw_peak_contact_force":0.48178,"subtask_id":"lift_object","tcp_end":[0.49473,-0.01552,0.20574],"tcp_start":[0.49014,-0.01538,0.04318],"tcp_to_object_dist_end":0.02531,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51804,0.03411,0.24937],"object_pos_start":[0.5026,-0.01593,0.18169],"object_to_goal_dist_end":0.1681,"object_to_goal_dist_start":0.22996,"object_z_max":0.24929,"peak_contact_force":0.09994,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37317.0,"raw_peak_contact_force":0.15207,"subtask_id":"transport_to_goal","tcp_end":[0.51453,0.03409,0.27849],"tcp_start":[0.49473,-0.01552,0.20574],"tcp_to_object_dist_end":0.02933,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57022,0.11697,0.14575],"object_pos_start":[0.51804,0.03411,0.24937],"object_to_goal_dist_end":0.1254,"object_to_goal_dist_start":0.1681,"object_z_max":0.24939,"peak_contact_force":0.0,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21435.0,"raw_peak_contact_force":0.36998,"subtask_id":"place_at_goal","tcp_end":[0.56205,0.14017,0.26413],"tcp_start":[0.51453,0.03409,0.27849],"tcp_to_object_dist_end":0.12091,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56312,0.12037,0.02578],"object_pos_start":[0.57022,0.11697,0.14575],"object_to_goal_dist_end":0.23346,"object_to_goal_dist_start":0.1254,"object_z_max":0.14575,"peak_contact_force":0.17349,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":496.0,"raw_peak_contact_force":2.17602,"subtask_id":"place_at_goal","tcp_end":[0.558,0.1392,0.28642],"tcp_start":[0.56205,0.14017,0.26413],"tcp_to_object_dist_end":0.26138,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07844,"approach_1.approach_z_offset":0.11355,"descend_1.descend_speed":0.04575,"descend_1.descend_z_offset":0.00751,"descend_to_place_1.place_speed":0.06853,"lift_1.lift_height":0.21178,"lift_1.lift_speed":0.09112,"transport_1.transport_height":0.21248,"transport_1.transport_speed":0.07886},"optimized_scores":{"best_composite_score":0.1013,"best_fitness_score":0.7013,"best_task_score":0.45198},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.60129,0.17083,-0.00753],"force_p95":1.194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50848,"mean_force":0.43701,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61489,0.167,0.1677]},{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.50959,0.03771,-0.00123],"force_p95":0.39983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62348,"mean_force":0.08871,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49696,0.03807,0.03414]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49984,0.05731,0.10639],"force_p95":0.08335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33497,"mean_force":0.0587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49951,0.03811,0.10363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20678.0,"contact_point_centroid":[0.50136,0.01918,0.10374],"force_p95":0.07858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30667,"mean_force":0.04967,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49941,0.03811,0.10214]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03968,-0.00213],"force_p95":0.1608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22034,"mean_force":0.1326,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4997,0.03831,0.03362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1322.0,"contact_point_centroid":[0.61358,0.18671,0.15718],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20446,"mean_force":0.0454,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61897,0.16822,0.15511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19055.0,"contact_point_centroid":[0.59103,0.11383,0.18992],"force_p95":0.07513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18742,"mean_force":0.04889,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58692,0.13245,0.18955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1251.0,"contact_point_centroid":[0.62244,0.14933,0.15491],"force_p95":0.07028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18521,"mean_force":0.04113,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61913,0.16826,0.15539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5139.0,"contact_point_centroid":[0.49999,0.0192,0.03388],"force_p95":0.06966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17926,"mean_force":0.04214,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49846,0.03821,0.03228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16454.0,"contact_point_centroid":[0.58526,0.15224,0.19173],"force_p95":0.08707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17647,"mean_force":0.05485,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58776,0.13335,0.18879]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50262,0.01757,0.22561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16168.0,"contact_point_centroid":[0.52461,0.0826,0.20829],"force_p95":0.08833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12875,"mean_force":0.06003,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52501,0.06349,0.20595]},{"body_a":"world","body_b":"grasp_target","contact_count":1492.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50582,0.03734,0.09604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18986.0,"contact_point_centroid":[0.52837,0.04484,0.20684],"force_p95":0.07753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11529,"mean_force":0.05178,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52499,0.06347,0.20592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4225.0,"contact_point_centroid":[0.49881,0.05753,0.03507],"force_p95":0.08314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09103,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49847,0.03821,0.03228]}],"total_contact_groups":15},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61043,0.16972,0.02718],"final_tcp_position":[0.6208,0.16863,0.15879],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":26.77498,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50755,0.03603,0.15126],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":26.77498,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1492.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50704,0.0389,0.0417],"tcp_start":[0.50755,0.03603,0.15126],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03885,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21304,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15811,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11164.0,"raw_peak_contact_force":0.22034,"subtask_id":"lift_object","tcp_end":[0.49843,0.03821,0.03225],"tcp_start":[0.50704,0.0389,0.0417],"tcp_to_object_dist_end":0.01559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51461,0.0392,0.16312],"object_pos_start":[0.51249,0.03885,0.02553],"object_to_goal_dist_end":0.17567,"object_to_goal_dist_start":0.21304,"object_z_max":0.16295,"peak_contact_force":0.08111,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37841.0,"raw_peak_contact_force":0.62348,"subtask_id":"lift_object","tcp_end":[0.50501,0.03838,0.17765],"tcp_start":[0.49843,0.03821,0.03225],"tcp_to_object_dist_end":0.01743,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55168,0.08722,0.21491],"object_pos_start":[0.51461,0.0392,0.16312],"object_to_goal_dist_end":0.13386,"object_to_goal_dist_start":0.17567,"object_z_max":0.21488,"peak_contact_force":0.08779,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35154.0,"raw_peak_contact_force":0.12875,"subtask_id":"transport_to_goal","tcp_end":[0.54555,0.08582,0.23524],"tcp_start":[0.50501,0.03838,0.17765],"tcp_to_object_dist_end":0.02128,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.61812,0.16973,0.13298],"object_pos_start":[0.55168,0.08722,0.21491],"object_to_goal_dist_end":0.01556,"object_to_goal_dist_start":0.13386,"object_z_max":0.21491,"peak_contact_force":0.07158,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":35509.0,"raw_peak_contact_force":0.18742,"subtask_id":"place_at_goal","tcp_end":[0.6208,0.16863,0.15879],"tcp_start":[0.54555,0.08582,0.23524],"tcp_to_object_dist_end":0.02597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61043,0.16972,0.02718],"object_pos_start":[0.61812,0.16973,0.13298],"object_to_goal_dist_end":0.11912,"object_to_goal_dist_start":0.01556,"object_z_max":0.13298,"peak_contact_force":0.3168,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2737.0,"raw_peak_contact_force":1.50848,"subtask_id":"place_at_goal","tcp_end":[0.6148,0.16698,0.17903],"tcp_start":[0.6208,0.16863,0.15879],"tcp_to_object_dist_end":0.15194,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25439,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04642,"approach_1.approach_z_offset":0.15847,"descend_1.descend_speed":0.04973,"descend_1.descend_z_offset":0.00503,"descend_to_place_1.place_speed":0.07027,"lift_1.lift_height":0.15477,"lift_1.lift_speed":0.08485,"transport_1.transport_height":0.18562,"transport_1.transport_speed":0.03345},"optimized_scores":{"best_composite_score":-0.01033,"best_fitness_score":0.58967,"best_task_score":0.22527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.54916,0.1841,-0.01257],"force_p95":1.57787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68193,"mean_force":0.79126,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55079,0.1866,0.25145]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47986,0.04635,-0.00125],"force_p95":0.37765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61398,"mean_force":0.08592,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46805,0.04679,0.03312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47155,0.06607,0.10039],"force_p95":0.08431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32182,"mean_force":0.05846,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47167,0.04688,0.09767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20870.0,"contact_point_centroid":[0.47367,0.02797,0.09833],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2925,"mean_force":0.04898,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47159,0.04687,0.09682]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04864,-0.00216],"force_p95":0.16664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23206,"mean_force":0.13432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47067,0.04708,0.03238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1054.0,"contact_point_centroid":[0.55201,0.20694,0.2368],"force_p95":0.07708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20077,"mean_force":0.04946,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55382,0.18776,0.23324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5070.0,"contact_point_centroid":[0.47129,0.02796,0.03243],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19336,"mean_force":0.04265,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46947,0.04696,0.03117]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.56246,0.17037,0.23402],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18968,"mean_force":0.0453,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55381,0.18776,0.23321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16701.0,"contact_point_centroid":[0.53598,0.12675,0.22958],"force_p95":0.08163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16307,"mean_force":0.05822,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.52926,0.14449,0.22945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14112.0,"contact_point_centroid":[0.52803,0.16471,0.23196],"force_p95":0.09239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1472,"mean_force":0.06664,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.53003,0.14579,0.22964]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48999,0.02048,0.24847]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.0451,0.11733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16716.0,"contact_point_centroid":[0.4885,0.09152,0.19902],"force_p95":0.08415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11539,"mean_force":0.05802,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48943,0.0724,0.19638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19599.0,"contact_point_centroid":[0.49304,0.05369,0.19739],"force_p95":0.07418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10109,"mean_force":0.04998,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4894,0.07235,0.19631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.46936,0.06629,0.03362],"force_p95":0.08679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46948,0.04696,0.03117]}],"total_contact_groups":15},"final_pose_error":0.05082,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5635,0.19038,0.01102],"final_tcp_position":[0.55516,0.18806,0.23619],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":26.34928,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48131,0.04272,0.19627],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":26.34928,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47782,0.04777,0.0397],"tcp_start":[0.48131,0.04272,0.19627],"tcp_to_object_dist_end":0.01456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04763,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29104,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16319,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11110.0,"raw_peak_contact_force":0.23206,"subtask_id":"lift_object","tcp_end":[0.46944,0.04695,0.03114],"tcp_start":[0.47782,0.04777,0.0397],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48763,0.04817,0.15325],"object_pos_start":[0.48272,0.04763,0.02546],"object_to_goal_dist_end":0.21793,"object_to_goal_dist_start":0.29104,"object_z_max":0.1531,"peak_contact_force":0.081,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38042.0,"raw_peak_contact_force":0.61398,"subtask_id":"lift_object","tcp_end":[0.47814,0.04722,0.16644],"tcp_start":[0.46944,0.04695,0.03114],"tcp_to_object_dist_end":0.01628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50853,0.09632,0.20785],"object_pos_start":[0.48763,0.04817,0.15325],"object_to_goal_dist_end":0.15315,"object_to_goal_dist_start":0.21793,"object_z_max":0.2078,"peak_contact_force":0.0889,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36315.0,"raw_peak_contact_force":0.11539,"subtask_id":"transport_to_goal","tcp_end":[0.50239,0.09485,0.22678],"tcp_start":[0.47814,0.04722,0.16644],"tcp_to_object_dist_end":0.01996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55993,0.19084,0.21246],"object_pos_start":[0.50853,0.09632,0.20785],"object_to_goal_dist_end":0.04745,"object_to_goal_dist_start":0.15315,"object_z_max":0.21245,"peak_contact_force":0.07954,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30813.0,"raw_peak_contact_force":0.16307,"subtask_id":"place_at_goal","tcp_end":[0.55516,0.18806,0.23619],"tcp_start":[0.50239,0.09485,0.22678],"tcp_to_object_dist_end":0.02436,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5635,0.19038,0.01102],"object_pos_start":[0.55993,0.19084,0.21246],"object_to_goal_dist_end":0.22357,"object_to_goal_dist_start":0.04745,"object_z_max":0.21246,"peak_contact_force":0.53641,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2321.0,"raw_peak_contact_force":1.68193,"subtask_id":"place_at_goal","tcp_end":[0.55074,0.18659,0.25839],"tcp_start":[0.55516,0.18806,0.23619],"tcp_to_object_dist_end":0.24773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```