## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.2073 | 0.15 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.1183 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.1152 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.0629 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | 0.6130 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.958, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=-0.207) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_target
  anchor: object
  target_entity: object
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_object
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: grasp_target
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: lift_clearance
- id: transport_to_goal
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
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (add)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (add)
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.207
- **task_score** (E): 0.150
- **fitness_score**: 0.183  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1783 |
| descend_grasp | 0.00 | 1.00 | 0.0483 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1884 |
| transport_to_goal | 0.00 | 1.00 | 0.1048 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.404, 0.019, 0.152) | (0.500, 0.024, 0.030)→(0.469, 0.027, 0.019) | 0.269→0.289 | 1.00 / 5.333 | 197.387 | 1400.933 |
| descend_grasp | descend | 0.00 / step_budget | (0.404, 0.019, 0.152)→(0.450, 0.017, 0.149) | (0.469, 0.027, 0.019)→(0.470, 0.027, 0.019) | 0.289→0.288 | 1.00 / 5.000 | 158.390 | 697.168 |
| grasp_1 | grasp | 1.00 / step_budget | (0.449, 0.016, 0.143)→(0.449, 0.016, 0.143) | (0.470, 0.027, 0.019)→(0.470, 0.027, 0.019) | 0.288→0.288 | 1.00 / 9.667 | 182017.334 | 62.765 |
| lift_object | lift | 1.00 / step_budget | (0.449, 0.016, 0.143)→(0.449, 0.016, 0.332) | (0.470, 0.027, 0.019)→(0.470, 0.027, 0.019) | 0.288→0.288 | 1.00 / 8.667 | 91002.936 | 179.415 |
| transport_to_goal | approach | 0.00 / step_budget | (0.449, 0.016, 0.332)→(0.517, 0.076, 0.364) | (0.470, 0.027, 0.019)→(0.470, 0.027, 0.019) | 0.288→0.288 | 1.00 / 9.000 | 3363.618 | 174.585 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.203
- phase_score: 0.056
- phase_breakdown.place_goal_score: 0.012
- phase_breakdown.lift_clearance_score: 0.053
- phase_breakdown.reach_object_score: 0.113
- phase_breakdown.grasp_target_score: 0.065
- grasp_place_fitness: 0.203

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.203
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.203
- **Median Q (composite search score)**: -0.217
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.12,"average_mean_iterations":29.272,"average_solve_count":125.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.05526,"descend_grasp.speed":0.06937,"lift_object.lift_height":0.19201,"transport_to_goal.arc_height":0.17163,"transport_to_goal.placement_z_offset":0.05261,"transport_to_goal.transport_speed":0.05195},"optimized_scores":{"best_composite_score":-0.21812,"best_fitness_score":0.17188,"best_task_score":0.1233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63793,0.00496,-0.00046],"force_p95":198.16264,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1461.5248,"mean_force":198.51149,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39819,0.00445,0.12474]},{"body_a":"world","body_b":"link6","contact_count":732.0,"contact_point_centroid":[0.64959,0.00253,-0.00024],"force_p95":407.6656,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":873.47589,"mean_force":272.76999,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4467,0.00158,0.18213]},{"body_a":"link5","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.52645,0.07951,0.11121],"force_p95":492.16337,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":495.57388,"mean_force":199.00999,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46529,-0.01261,0.15471]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53101,0.00785,-0.0033],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":380.36242,"mean_force":16.5375,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37865,0.00329,0.04861]},{"body_a":"world","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.65492,0.09313,-6e-05],"force_p95":156.27318,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.36391,"mean_force":103.54773,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4651,-0.02017,0.14487]},{"body_a":"link5","body_b":"hand","contact_count":1072.0,"contact_point_centroid":[0.52154,0.08278,0.30644],"force_p95":89.4598,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.32413,"mean_force":63.97968,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49104,-0.02066,0.33915]},{"body_a":"link5","body_b":"hand","contact_count":554.0,"contact_point_centroid":[0.52842,0.07428,0.10166],"force_p95":48.65829,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.62211,"mean_force":20.44661,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.02014,0.14539]},{"body_a":"world","body_b":"link5","contact_count":476.0,"contact_point_centroid":[0.65495,0.09305,-8e-05],"force_p95":59.49203,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.16122,"mean_force":45.87719,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46511,-0.02023,0.14486]},{"body_a":"grasp_target","body_b":"link7","contact_count":848.0,"contact_point_centroid":[0.49626,-0.01985,0.04858],"force_p95":0.77144,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.00461,"mean_force":0.26192,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39767,0.0044,0.12245]},{"body_a":"grasp_target","body_b":"hand","contact_count":512.0,"contact_point_centroid":[0.49147,-0.03012,0.05689],"force_p95":1.61477,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.304,"mean_force":0.40556,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39381,0.00403,0.1083]},{"body_a":"world","body_b":"grasp_target","contact_count":2281.0,"contact_point_centroid":[0.48651,-0.01759,-0.00389],"force_p95":0.40218,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.47633,"mean_force":0.26792,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41777,0.00411,0.13992]},{"body_a":"world","body_b":"grasp_target","contact_count":3144.0,"contact_point_centroid":[0.49587,-0.01495,-0.00199],"force_p95":0.12539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1698,"mean_force":0.12255,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4479,0.0011,0.18072]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49587,-0.01495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.02017,0.14532]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.49587,-0.01495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46441,-0.02047,0.23018]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49587,-0.01495,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49127,-0.02089,0.33887]},{"body_a":"grasp_target","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50932,0.00095,0.05686],"force_p95":0.06627,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08283,"mean_force":0.01657,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.40958,0.00506,0.15739]}],"total_contact_groups":20},"final_pose_error":0.23138,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49587,-0.01495,0.02602],"final_tcp_position":[0.5184,-0.02823,0.34894],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1461.5248,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,-0.01509,0.02566],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31493,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":188.90924,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4551.0,"raw_peak_contact_force":1461.5248,"subtask_id":"reach_object","tcp_end":[0.40944,0.00507,0.15716],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.49587,-0.01495,0.02602],"object_pos_start":[0.4938,-0.01509,0.02566],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31493,"object_z_max":0.02605,"peak_contact_force":183.09051,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3900.0,"raw_peak_contact_force":873.47589,"subtask_id":"grasp_target","tcp_end":[0.46669,-0.01594,0.15362],"tcp_start":[0.40944,0.00507,0.15716],"tcp_to_object_dist_end":0.1309,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49587,-0.01495,0.02602],"object_pos_start":[0.49587,-0.01495,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":43.76199,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4013.0,"raw_peak_contact_force":87.62211,"tcp_end":[0.46512,-0.02015,0.14483],"tcp_start":[0.46512,-0.02017,0.14483],"tcp_to_object_dist_end":0.12284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.49587,-0.01495,0.02602],"object_pos_start":[0.49587,-0.01495,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4507.0,"raw_peak_contact_force":157.36391,"subtask_id":"lift_clearance","tcp_end":[0.46471,-0.01996,0.31708],"tcp_start":[0.46512,-0.02015,0.14483],"tcp_to_object_dist_end":0.29277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49587,-0.01495,0.02602],"object_pos_start":[0.49587,-0.01495,0.02602],"object_to_goal_dist_end":0.31398,"object_to_goal_dist_start":0.31398,"object_z_max":0.02602,"peak_contact_force":73.54394,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9518.0,"raw_peak_contact_force":142.32413,"subtask_id":"place_goal","tcp_end":[0.5184,-0.02823,0.34894],"tcp_start":[0.46471,-0.01996,0.31708],"tcp_to_object_dist_end":0.32397,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":68.0,"average_failure_rate":0.36559,"average_mean_iterations":77.22043,"average_solve_count":186.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.05205,"descend_grasp.speed":0.06739,"lift_object.lift_height":0.18688,"transport_to_goal.arc_height":0.15738,"transport_to_goal.placement_z_offset":0.01872,"transport_to_goal.transport_speed":0.0543},"optimized_scores":{"best_composite_score":-0.18714,"best_fitness_score":0.20286,"best_task_score":0.2032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63598,0.0184,-0.00048],"force_p95":203.61783,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1443.10671,"mean_force":205.81967,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39757,0.01726,0.12807]},{"body_a":"world","body_b":"link6","contact_count":961.0,"contact_point_centroid":[0.64825,0.0312,-0.00023],"force_p95":362.32412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":897.0422,"mean_force":276.32257,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4472,0.02898,0.18447]},{"body_a":"link5","body_b":"hand","contact_count":188.0,"contact_point_centroid":[0.54863,0.01903,0.29085],"force_p95":358.49595,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":381.30798,"mean_force":301.1183,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52107,0.09071,0.34101]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.70204,0.0503,-2e-05],"force_p95":259.26247,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.98069,"mean_force":151.12098,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4638,0.03636,0.15111]},{"body_a":"world","body_b":"link6","contact_count":415.0,"contact_point_centroid":[0.70207,0.05029,-3e-05],"force_p95":13.39763,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.52075,"mean_force":10.89458,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46379,0.03629,0.15103]},{"body_a":"grasp_target","body_b":"link7","contact_count":219.0,"contact_point_centroid":[0.49507,0.02251,0.03423],"force_p95":3.23636,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.8177,"mean_force":0.62545,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38896,0.01209,0.09519]},{"body_a":"grasp_target","body_b":"hand","contact_count":186.0,"contact_point_centroid":[0.48435,0.02311,0.04958],"force_p95":2.57945,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.11097,"mean_force":0.6276,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38843,0.0119,0.09165]},{"body_a":"world","body_b":"grasp_target","contact_count":3513.0,"contact_point_centroid":[0.47984,0.04537,-0.00261],"force_p95":0.40134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48241,"mean_force":0.17769,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41139,0.01676,0.14072]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47065,0.04655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44788,0.02901,0.18366]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47065,0.04655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46417,0.0362,0.15196]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.47065,0.04655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46318,0.03659,0.23406]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.47065,0.04655,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50335,0.07287,0.33557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":775.0,"contact_point_centroid":[0.4658,0.03651,0.14974],"force_p95":0.01341,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01066,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4638,0.0363,0.15103]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2276.0,"contact_point_centroid":[0.46513,0.03679,0.23315],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01025,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46318,0.03659,0.23438]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1442.0,"contact_point_centroid":[0.50556,0.07334,0.33438],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01029,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50356,0.07309,0.33561]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53094,0.01722,-0.00351],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37735,0.01103,0.04952]}],"total_contact_groups":16},"final_pose_error":0.2038,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47065,0.04655,0.01602],"final_tcp_position":[0.54055,0.11522,0.3389],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.12077,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47065,0.04655,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23903,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":200.21531,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4825.0,"raw_peak_contact_force":1443.10671,"subtask_id":"reach_object","tcp_end":[0.40883,0.02528,0.16025],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15836,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47065,0.04655,0.01602],"object_pos_start":[0.47065,0.04655,0.01602],"object_to_goal_dist_end":0.23903,"object_to_goal_dist_start":0.23903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4961.0,"raw_peak_contact_force":897.0422,"subtask_id":"grasp_target","tcp_end":[0.46668,0.03536,0.15863],"tcp_start":[0.40883,0.02528,0.16025],"tcp_to_object_dist_end":0.1431,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47065,0.04655,0.01602],"object_pos_start":[0.47065,0.04655,0.01602],"object_to_goal_dist_end":0.23903,"object_to_goal_dist_start":0.23903,"object_z_max":0.01602,"peak_contact_force":273004.12076,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3390.0,"raw_peak_contact_force":14.52075,"tcp_end":[0.4638,0.03629,0.15103],"tcp_start":[0.4638,0.0363,0.15103],"tcp_to_object_dist_end":0.13557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.47065,0.04655,0.01602],"object_pos_start":[0.47065,0.04655,0.01602],"object_to_goal_dist_end":0.23903,"object_to_goal_dist_start":0.23903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4368.0,"raw_peak_contact_force":272.98069,"subtask_id":"lift_clearance","tcp_end":[0.46339,0.03607,0.31801],"tcp_start":[0.4638,0.03629,0.15103],"tcp_to_object_dist_end":0.30226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.47065,0.04655,0.01602],"object_pos_start":[0.47065,0.04655,0.01602],"object_to_goal_dist_end":0.23903,"object_to_goal_dist_start":0.23903,"object_z_max":0.01602,"peak_contact_force":268.37916,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2962.0,"raw_peak_contact_force":381.30798,"subtask_id":"place_goal","tcp_end":[0.54055,0.11522,0.3389],"tcp_start":[0.46339,0.03607,0.31801],"tcp_to_object_dist_end":0.33742,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28931,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.04589,"descend_grasp.speed":0.01214,"lift_object.lift_height":0.24571,"transport_to_goal.arc_height":0.13626,"transport_to_goal.placement_z_offset":0.0269,"transport_to_goal.transport_speed":0.01578},"optimized_scores":{"best_composite_score":-0.21677,"best_fitness_score":0.17323,"best_task_score":0.12492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.6335,0.01937,-0.00046],"force_p95":204.50625,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1298.1669,"mean_force":206.47129,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38864,0.01809,0.11591]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52591,0.01789,-0.00304],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1201.43393,"mean_force":54.61063,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37383,0.01195,0.04933]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.64203,0.02926,-0.00031],"force_p95":295.22428,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.98557,"mean_force":282.4205,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.41134,0.02938,0.1454]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.65612,0.03217,-0.0001],"force_p95":105.33583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.9015,"mean_force":89.2456,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41848,0.03196,0.13441]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65593,0.03221,-0.00013],"force_p95":81.58933,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.15192,"mean_force":70.4823,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41841,0.03199,0.13454]},{"body_a":"grasp_target","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.46018,0.04654,0.04007],"force_p95":3.93502,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.24182,"mean_force":1.62982,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38201,0.01209,0.05595]},{"body_a":"grasp_target","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.48651,0.02925,0.01101],"force_p95":0.95699,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.59814,"mean_force":0.50661,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37504,0.01206,0.05816]},{"body_a":"world","body_b":"grasp_target","contact_count":3883.0,"contact_point_centroid":[0.44741,0.05033,-0.00217],"force_p95":0.13845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38165,"mean_force":0.14166,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40113,0.01717,0.12668]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44201,0.05054,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.41134,0.02938,0.1454]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44201,0.05054,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41841,0.03199,0.13454]},{"body_a":"world","body_b":"grasp_target","contact_count":2756.0,"contact_point_centroid":[0.44201,0.05054,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41719,0.03185,0.24643]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44201,0.05054,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46257,0.08773,0.39156]},{"body_a":"left_finger","body_b":"right_finger","contact_count":748.0,"contact_point_centroid":[0.42053,0.03197,0.13349],"force_p95":0.01294,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01099,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41849,0.03197,0.13439]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4285.0,"contact_point_centroid":[0.46462,0.08775,0.39093],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01041,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46266,0.08785,0.39159]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2916.0,"contact_point_centroid":[0.41913,0.03184,0.24588],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01107,"mean_force":0.01053,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41719,0.03185,0.24676]}],"total_contact_groups":15},"final_pose_error":0.19246,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44201,0.05054,0.01602],"final_tcp_position":[0.49299,0.14084,0.40365],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273008.56374,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44201,0.05054,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":203.03537,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4876.0,"raw_peak_contact_force":1298.1669,"subtask_id":"reach_object","tcp_end":[0.39376,0.0259,0.13845],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13388,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44201,0.05054,0.01602],"object_pos_start":[0.44201,0.05054,0.01602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31201,"object_z_max":0.01602,"peak_contact_force":291.95593,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":320.98557,"subtask_id":"grasp_target","tcp_end":[0.41795,0.03201,0.13496],"tcp_start":[0.39376,0.0259,0.13845],"tcp_to_object_dist_end":0.12276,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44201,0.05054,0.01602],"object_pos_start":[0.44201,0.05054,0.01602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31201,"object_z_max":0.01602,"peak_contact_force":273004.12065,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3498.0,"raw_peak_contact_force":86.15192,"tcp_end":[0.41849,0.03196,0.13439],"tcp_start":[0.41849,0.03197,0.13439],"tcp_to_object_dist_end":0.1221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.44201,0.05054,0.01602],"object_pos_start":[0.44201,0.05054,0.01602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31201,"object_z_max":0.01602,"peak_contact_force":273008.56374,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5676.0,"raw_peak_contact_force":107.9015,"subtask_id":"lift_clearance","tcp_end":[0.41833,0.03197,0.36032],"tcp_start":[0.41849,0.03196,0.13439],"tcp_to_object_dist_end":0.34561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44201,0.05054,0.01602],"object_pos_start":[0.44201,0.05054,0.01602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31201,"object_z_max":0.01602,"peak_contact_force":9748.93147,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8285.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.49299,0.14084,0.40365],"tcp_start":[0.41833,0.03197,0.36032],"tcp_to_object_dist_end":0.40126,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```