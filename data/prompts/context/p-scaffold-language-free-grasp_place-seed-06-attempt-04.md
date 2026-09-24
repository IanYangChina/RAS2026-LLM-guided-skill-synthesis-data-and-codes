## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3980 | 0.29 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0208 | 0.30 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3194 | 0.17 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

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

## Current Skill (Q=-0.398) — your mutation base

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

- **Composite score**: -0.398
- **task_score** (E): 0.290
- **fitness_score**: 0.602  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1000 |
| descend_1 | 1.00 | 1.00 | 0.1457 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| lift_1 | 0.67 | 1.00 | 0.1501 |
| transport_1 | 1.00 | 1.00 | 0.2662 |
| descend_to_place_1 | 1.00 | 1.00 | 0.1316 |
| release_1 | 1.00 | 1.00 | 0.0188 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.019, 0.205) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.019, 0.205)→(0.495, 0.024, 0.060) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 7.041 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.060)→(0.487, 0.023, 0.051) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 37.000 | 0.149 | 0.187 |
| lift_1 | lift | 0.67 / step_budget | (0.487, 0.023, 0.051)→(0.494, 0.023, 0.201) | (0.500, 0.024, 0.026)→(0.501, 0.024, 0.171) | 0.272→0.206 | 1.00 / 28.333 | 0.099 | 0.353 |
| transport_1 | approach | 1.00 / step_budget | (0.494, 0.023, 0.201)→(0.589, 0.181, 0.385) | (0.501, 0.024, 0.171)→(0.585, 0.154, 0.228) | 0.206→0.165 | 1.00 / 17.333 | 91002.836 | 0.952 |
| descend_to_place_1 | descend | 1.00 / step_budget | (0.589, 0.181, 0.385)→(0.595, 0.192, 0.254) | (0.585, 0.154, 0.228)→(0.592, 0.162, 0.151) | 0.165→0.087 | 1.00 / 15.000 | 0.135 | 0.377 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.192, 0.254)→(0.590, 0.190, 0.272) | (0.592, 0.162, 0.151)→(0.586, 0.172, 0.023) | 0.087→0.194 | 1.00 / 3.333 | 0.191 | 1.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.428
- phase_score: 0.369
- phase_breakdown.approach_object_score: 0.223
- phase_breakdown.transport_to_goal_score: 0.440
- phase_breakdown.lift_object_score: 0.472
- phase_breakdown.place_at_goal_score: 0.328
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.428
- **Median Q (composite search score)**: -0.432
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79439,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07717,"approach_1.approach_tolerance":0.02529,"approach_1.approach_z_offset":0.18477,"descend_1.descend_speed":0.0658,"descend_1.descend_tolerance":0.00523,"descend_1.descend_z_offset":0.0324,"descend_to_place_1.place_speed":0.10507,"descend_to_place_1.place_tolerance":0.04116,"descend_to_place_1.place_z_offset":0.02446,"grasp_1.grasp_timeout":1.2842,"lift_1.lift_height":0.27412,"lift_1.lift_speed":0.08389,"lift_1.lift_tolerance":0.02505,"release_1.release_timeout":1.59194,"transport_1.transport_height":0.15787,"transport_1.transport_speed":0.10785,"transport_1.transport_tolerance":0.02698},"optimized_scores":{"best_composite_score":-0.43183,"best_fitness_score":0.56817,"best_task_score":0.22234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":238.0,"contact_point_centroid":[0.56907,0.2125,-0.00788],"force_p95":1.26949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96766,"mean_force":0.367,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57961,0.17916,0.32077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":737.0,"contact_point_centroid":[0.57969,0.19322,0.35283],"force_p95":0.16361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46299,"mean_force":0.11161,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58081,0.17487,0.35648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":571.0,"contact_point_centroid":[0.58942,0.15856,0.35142],"force_p95":0.17995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42026,"mean_force":0.12999,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.58086,0.17498,0.35566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.5911,0.16431,0.30073],"force_p95":0.30191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39485,"mean_force":0.18786,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58219,0.18027,0.30562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":317.0,"contact_point_centroid":[0.58097,0.19781,0.30057],"force_p95":0.21038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37448,"mean_force":0.11892,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58184,0.18012,0.30446]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.50042,-0.01512,-0.00145],"force_p95":0.34358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35877,"mean_force":0.12082,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4897,-0.01536,0.05198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8115.0,"contact_point_centroid":[0.49361,-0.03433,0.14861],"force_p95":0.10867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31362,"mean_force":0.07104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49291,-0.01543,0.14951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8694.0,"contact_point_centroid":[0.49382,0.00333,0.14893],"force_p95":0.10936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28425,"mean_force":0.06778,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49296,-0.01543,0.1504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5017.0,"contact_point_centroid":[0.54289,0.0575,0.32483],"force_p95":0.14114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.258,"mean_force":0.09907,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53796,0.07551,0.32838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5962.0,"contact_point_centroid":[0.53843,0.09572,0.3267],"force_p95":0.11966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23489,"mean_force":0.07905,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53879,0.07747,0.32958]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01569,-0.00204],"force_p95":0.13482,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1552,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49187,-0.01537,0.0522]},{"body_a":"world","body_b":"grasp_target","contact_count":416.0,"contact_point_centroid":[0.50382,-0.01567,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12383,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50004,-0.00469,0.27175]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49824,-0.01297,0.14387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4375.0,"contact_point_centroid":[0.4917,0.00359,0.05044],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09745,"mean_force":0.05014,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01536,0.05089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4151.0,"contact_point_centroid":[0.49195,-0.03448,0.05082],"force_p95":0.08474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09096,"mean_force":0.05219,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01536,0.05089]}],"total_contact_groups":15},"final_pose_error":0.0408,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56801,0.21601,0.0252],"final_tcp_position":[0.58333,0.18045,0.31261],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.96766,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12232,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50049,-0.01033,0.23898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3756.0,"raw_peak_contact_force":0.12264,"subtask_id":"approach_object","tcp_end":[0.4988,-0.01542,0.05987],"tcp_start":[0.50049,-0.01033,0.23898],"tcp_to_object_dist_end":0.03422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.0156,0.02577],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31238,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13579,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10326.0,"raw_peak_contact_force":0.1552,"subtask_id":"lift_object","tcp_end":[0.49064,-0.01536,0.05086],"tcp_start":[0.4988,-0.01542,0.05987],"tcp_to_object_dist_end":0.02831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.50899,-0.01591,0.24545],"object_pos_start":[0.50376,-0.0156,0.02577],"object_to_goal_dist_end":0.21779,"object_to_goal_dist_start":0.31238,"object_z_max":0.24508,"peak_contact_force":0.1041,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16877.0,"raw_peak_contact_force":0.35877,"subtask_id":"lift_object","tcp_end":[0.50039,-0.01554,0.27543],"tcp_start":[0.49064,-0.01536,0.05086],"tcp_to_object_dist_end":0.03119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.5852,0.17257,0.35327],"object_pos_start":[0.50899,-0.01591,0.24545],"object_to_goal_dist_end":0.10621,"object_to_goal_dist_start":0.21779,"object_z_max":0.35307,"peak_contact_force":0.14485,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10979.0,"raw_peak_contact_force":0.258,"subtask_id":"transport_to_goal","tcp_end":[0.57876,0.17006,0.38758],"tcp_start":[0.50039,-0.01554,0.27543],"tcp_to_object_dist_end":0.03501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.58893,0.18379,0.27702],"object_pos_start":[0.5852,0.17257,0.35327],"object_to_goal_dist_end":0.0292,"object_to_goal_dist_start":0.10621,"object_z_max":0.35332,"peak_contact_force":0.14511,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.46299,"subtask_id":"place_at_goal","tcp_end":[0.58333,0.18045,0.31261],"tcp_start":[0.57876,0.17006,0.38758],"tcp_to_object_dist_end":0.03618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56801,0.21601,0.0252],"object_pos_start":[0.58893,0.18379,0.27702],"object_to_goal_dist_end":0.22553,"object_to_goal_dist_start":0.0292,"object_z_max":0.27702,"peak_contact_force":0.07472,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":707.0,"raw_peak_contact_force":1.96766,"subtask_id":"place_at_goal","tcp_end":[0.57958,0.17915,0.32975],"tcp_start":[0.58333,0.18045,0.31261],"tcp_to_object_dist_end":0.30699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28169,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02978,"approach_1.approach_tolerance":0.03948,"approach_1.approach_z_offset":0.12621,"descend_1.descend_speed":0.06377,"descend_1.descend_tolerance":0.00513,"descend_1.descend_z_offset":0.03275,"descend_to_place_1.place_speed":0.14171,"descend_to_place_1.place_tolerance":0.03075,"descend_to_place_1.place_z_offset":0.00718,"grasp_1.grasp_timeout":0.78715,"lift_1.lift_height":0.18882,"lift_1.lift_speed":0.05706,"lift_1.lift_tolerance":0.01121,"release_1.release_timeout":1.43824,"transport_1.transport_height":0.21602,"transport_1.transport_speed":0.08251,"transport_1.transport_tolerance":0.03566},"optimized_scores":{"best_composite_score":-0.32367,"best_fitness_score":0.67633,"best_task_score":0.4275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.61166,0.17559,-0.00956],"force_p95":1.50332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62475,"mean_force":0.67774,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61562,0.167,0.18917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.62592,0.15108,0.16965],"force_p95":0.14214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51949,"mean_force":0.08951,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61911,0.16809,0.17427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":807.0,"contact_point_centroid":[0.61768,0.18699,0.17199],"force_p95":0.17301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51091,"mean_force":0.09096,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61898,0.16805,0.1741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2053.0,"contact_point_centroid":[0.61668,0.1824,0.26001],"force_p95":0.17905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41479,"mean_force":0.10246,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.61775,0.16361,0.26132]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.50881,0.03759,-0.00121],"force_p95":0.26446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39018,"mean_force":0.07588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49787,0.03835,0.0477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.62473,0.14649,0.26137],"force_p95":0.17599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31151,"mean_force":0.09881,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.6176,0.16343,0.26437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19700.0,"contact_point_centroid":[0.49896,0.05749,0.09592],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24453,"mean_force":0.05102,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49914,0.03835,0.09373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20083.0,"contact_point_centroid":[0.50047,0.01926,0.09441],"force_p95":0.07901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23641,"mean_force":0.05041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49912,0.03835,0.09355]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03974,-0.0021],"force_p95":0.15102,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19618,"mean_force":0.13011,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03858,0.04742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7128.0,"contact_point_centroid":[0.55103,0.11197,0.22743],"force_p95":0.10163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1755,"mean_force":0.06119,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5522,0.09299,0.22664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7580.0,"contact_point_centroid":[0.55812,0.07697,0.23006],"force_p95":0.10106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17045,"mean_force":0.05938,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5546,0.09555,0.2307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4647.0,"contact_point_centroid":[0.50103,0.01941,0.0467],"force_p95":0.07683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14912,"mean_force":0.04707,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03848,0.04606]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.51251,0.03972,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5028,0.01192,0.25349]},{"body_a":"world","body_b":"grasp_target","contact_count":3480.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50587,0.03423,0.11259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4695.0,"contact_point_centroid":[0.49935,0.05771,0.04899],"force_p95":0.07921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08014,"mean_force":0.04651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03848,0.04606]}],"total_contact_groups":15},"final_pose_error":0.03069,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62966,0.16986,0.0176],"final_tcp_position":[0.6222,0.16885,0.1822],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.62475,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":576.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50714,0.02791,0.19321],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3480.0,"raw_peak_contact_force":0.12264,"subtask_id":"approach_object","tcp_end":[0.50741,0.03913,0.0552],"tcp_start":[0.50714,0.02791,0.19321],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03917,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21278,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15022,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11142.0,"raw_peak_contact_force":0.19618,"subtask_id":"lift_object","tcp_end":[0.49925,0.03847,0.04602],"tcp_start":[0.50741,0.03913,0.0552],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50866,0.03933,0.11695],"object_pos_start":[0.5125,0.03917,0.02564],"object_to_goal_dist_end":0.18074,"object_to_goal_dist_start":0.21278,"object_z_max":0.11684,"peak_contact_force":0.07937,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39949.0,"raw_peak_contact_force":0.39018,"subtask_id":"lift_object","tcp_end":[0.50326,0.03857,0.14365],"tcp_start":[0.49925,0.03847,0.04602],"tcp_to_object_dist_end":0.02725,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.62594,0.16302,0.30353],"object_pos_start":[0.50866,0.03933,0.11695],"object_to_goal_dist_end":0.1588,"object_to_goal_dist_start":0.18074,"object_z_max":0.30311,"peak_contact_force":0.11431,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14708.0,"raw_peak_contact_force":0.1755,"subtask_id":"transport_to_goal","tcp_end":[0.61399,0.15879,0.33125],"tcp_start":[0.50326,0.03857,0.14365],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.62716,0.17224,0.14999],"object_pos_start":[0.62594,0.16302,0.30353],"object_to_goal_dist_end":0.00499,"object_to_goal_dist_start":0.1588,"object_z_max":0.30403,"peak_contact_force":0.13826,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4245.0,"raw_peak_contact_force":0.41479,"subtask_id":"place_at_goal","tcp_end":[0.6222,0.16885,0.1822],"tcp_start":[0.61399,0.15879,0.33125],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62966,0.16986,0.0176],"object_pos_start":[0.62716,0.17224,0.14999],"object_to_goal_dist_end":0.12747,"object_to_goal_dist_start":0.00499,"object_z_max":0.14999,"peak_contact_force":0.37502,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1677.0,"raw_peak_contact_force":1.62475,"subtask_id":"place_at_goal","tcp_end":[0.61555,0.16699,0.1992],"tcp_start":[0.6222,0.16885,0.1822],"tcp_to_object_dist_end":0.18217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44251,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04895,"approach_1.approach_tolerance":0.02119,"approach_1.approach_z_offset":0.13409,"descend_1.descend_speed":0.03065,"descend_1.descend_tolerance":0.00879,"descend_1.descend_z_offset":0.03037,"descend_to_place_1.place_speed":0.0916,"descend_to_place_1.place_tolerance":0.01736,"descend_to_place_1.place_z_offset":0.02041,"grasp_1.grasp_timeout":1.17617,"lift_1.lift_height":0.18713,"lift_1.lift_speed":0.07764,"lift_1.lift_tolerance":0.03056,"release_1.release_timeout":1.26283,"transport_1.transport_height":0.23448,"transport_1.transport_speed":0.12389,"transport_1.transport_tolerance":0.03269},"optimized_scores":{"best_composite_score":-0.43864,"best_fitness_score":0.56136,"best_task_score":0.21935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":355.0,"contact_point_centroid":[0.54872,0.12834,-0.00679],"force_p95":1.30297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42368,"mean_force":0.36562,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55962,0.19062,0.39886]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.48008,0.0467,-0.00157],"force_p95":0.26091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31066,"mean_force":0.10529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46924,0.04656,0.05622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2982.0,"contact_point_centroid":[0.49746,0.10566,0.23713],"force_p95":0.14598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29938,"mean_force":0.0942,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.08721,0.24099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.50498,0.0747,0.24443],"force_p95":0.14822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2704,"mean_force":0.0942,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50246,0.09244,0.2489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3131.0,"contact_point_centroid":[0.47082,0.06523,0.11191],"force_p95":0.11948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26695,"mean_force":0.08619,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47232,0.04676,0.11478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.47412,0.02822,0.11518],"force_p95":0.14532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26685,"mean_force":0.09547,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47266,0.04678,0.11916]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.55789,0.13035,-0.00239],"force_p95":0.24492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25413,"mean_force":0.14651,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.5764,0.22107,0.3431]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04868,-0.00214],"force_p95":0.16356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2109,"mean_force":0.13305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47128,0.04678,0.05633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2887.0,"contact_point_centroid":[0.47058,0.02796,0.0512],"force_p95":0.10945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17922,"mean_force":0.07116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47012,0.04667,0.05511]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49111,0.01885,0.24323]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56125,0.13111,-0.00199],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12304,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57556,0.22481,0.26767]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47893,0.04351,0.12225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3479.0,"contact_point_centroid":[0.46982,0.06558,0.05263],"force_p95":0.1014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10247,"mean_force":0.06035,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47013,0.04667,0.05512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":589.0,"contact_point_centroid":[0.56174,0.19497,0.40804],"force_p95":0.01322,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01076,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56234,0.19523,0.40595]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1428.0,"contact_point_centroid":[0.57571,0.22016,0.35584],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place_1","phase_type":"descend","tcp_position_centroid":[0.57612,0.22043,0.35358]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.57737,0.22541,0.26566],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00987,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57727,0.22557,0.26321]}],"total_contact_groups":16},"final_pose_error":0.01716,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56125,0.13111,0.02602],"final_tcp_position":[0.57864,0.22613,0.26753],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273008.24892,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48267,0.03989,0.18282],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":20.87816,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.47811,0.04742,0.06364],"tcp_start":[0.48267,0.03989,0.18282],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48281,0.04768,0.0255],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29096,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15981,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8166.0,"raw_peak_contact_force":0.2109,"subtask_id":"lift_object","tcp_end":[0.4701,0.04667,0.05508],"tcp_start":[0.47811,0.04742,0.06364],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.48644,0.04822,0.1502],"object_pos_start":[0.48281,0.04768,0.0255],"object_to_goal_dist_end":0.2195,"object_to_goal_dist_start":0.29096,"object_z_max":0.14971,"peak_contact_force":0.11401,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5965.0,"raw_peak_contact_force":0.31066,"subtask_id":"lift_object","tcp_end":[0.47793,0.0472,0.18268],"tcp_start":[0.4701,0.04667,0.05508],"tcp_to_object_dist_end":0.03359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.54459,0.1275,0.02781],"object_pos_start":[0.48644,0.04822,0.1502],"object_to_goal_dist_end":0.22966,"object_to_goal_dist_start":0.2195,"object_z_max":0.27499,"peak_contact_force":273008.24892,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7054.0,"raw_peak_contact_force":2.42368,"subtask_id":"transport_to_goal","tcp_end":[0.57411,0.21521,0.43661],"tcp_start":[0.47793,0.0472,0.18268],"tcp_to_object_dist_end":0.41915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.56127,0.13111,0.02602],"object_pos_start":[0.54459,0.1275,0.02781],"object_to_goal_dist_end":0.22756,"object_to_goal_dist_start":0.22966,"object_z_max":0.02804,"peak_contact_force":0.12305,"phase_name":"descend_to_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.25413,"subtask_id":"place_at_goal","tcp_end":[0.57864,0.22613,0.26753],"tcp_start":[0.57411,0.21521,0.43661],"tcp_to_object_dist_end":0.26011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56125,0.13111,0.02602],"object_pos_start":[0.56127,0.13111,0.02602],"object_to_goal_dist_end":0.22757,"object_to_goal_dist_start":0.22756,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12304,"subtask_id":"place_at_goal","tcp_end":[0.57459,0.22436,0.28761],"tcp_start":[0.57864,0.22613,0.26753],"tcp_to_object_dist_end":0.27803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```