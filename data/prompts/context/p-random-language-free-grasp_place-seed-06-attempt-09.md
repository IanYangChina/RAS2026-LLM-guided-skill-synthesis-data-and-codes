## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.0629 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | 0.6130 | 0.96 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2698 | 0.29 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2333 | 0.25 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2261 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.063) — your mutation base

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

- **Composite score**: -0.063
- **task_score** (E): 0.170
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0780 |
| descend_grasp | 1.00 | 1.00 | 0.1532 |
| grasp_1 | 1.00 | 1.00 | 0.0183 |
| lift_object | 1.00 | 1.00 | 0.1453 |
| transport_to_goal | 1.00 | 1.00 | 0.2007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.020, 0.228) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.272 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, 0.020, 0.228)→(0.499, 0.023, 0.075) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.272→0.271 | 1.00 / 4.000 | 28.590 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.499, 0.023, 0.075)→(0.488, 0.023, 0.060) | (0.500, 0.024, 0.026)→(0.500, 0.021, 0.023) | 0.271→0.275 | 1.00 / 20.000 | 0.354 | 0.382 |
| lift_object | lift | 1.00 / step_budget | (0.488, 0.023, 0.060)→(0.485, 0.022, 0.205) | (0.500, 0.021, 0.023)→(0.500, 0.023, 0.026) | 0.275→0.272 | 1.00 / 8.000 | 0.123 | 0.451 |
| transport_to_goal | approach | 1.00 / step_budget | (0.485, 0.022, 0.205)→(0.586, 0.178, 0.246) | (0.500, 0.023, 0.026)→(0.500, 0.023, 0.026) | 0.272→0.272 | 1.00 / 8.333 | 91006.786 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.242
- phase_score: 0.326
- phase_breakdown.place_goal_score: 0.378
- phase_breakdown.lift_clearance_score: 0.316
- phase_breakdown.reach_object_score: 0.137
- phase_breakdown.grasp_target_score: 0.407
- grasp_place_fitness: 0.313

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.313
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.242
- **Median Q (composite search score)**: -0.077
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.255


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42358,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07779,"lift_object.lift_height":0.16447,"transport_to_goal.arc_height":0.08513,"transport_to_goal.placement_z_offset":0.00688,"transport_to_goal.transport_speed":0.02083},"optimized_scores":{"best_composite_score":-0.0852,"best_fitness_score":0.2548,"best_task_score":0.12576},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":945.0,"contact_point_centroid":[0.50408,-0.01147,-0.0022],"force_p95":0.21049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44647,"mean_force":0.13228,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48804,-0.01219,0.13159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.49179,-0.01722,0.05578],"force_p95":0.20325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4378,"mean_force":0.09523,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48998,-0.01222,0.06102]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50401,-0.01542,-0.00252],"force_p95":0.36153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37987,"mean_force":0.16606,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49219,-0.01223,0.06113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":691.0,"contact_point_centroid":[0.49633,-0.00242,0.05338],"force_p95":0.18306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24721,"mean_force":0.08931,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49112,-0.01223,0.06004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.49431,-0.00739,0.05495],"force_p95":0.20243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22161,"mean_force":0.12299,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48982,-0.01222,0.06147]},{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.50382,-0.01567,-0.00158],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1245,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50153,0.0006,0.26878]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.50408,-0.01389,-0.00199],"force_p95":0.12278,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.123,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52099,0.05687,0.26977]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12251,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50221,-0.00748,0.15353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3099.0,"contact_point_centroid":[0.49109,-0.02298,0.05508],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09355,"mean_force":0.03694,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49112,-0.01222,0.06004]},{"body_a":"left_finger","body_b":"right_finger","contact_count":625.0,"contact_point_centroid":[0.48822,-0.01219,0.15787],"force_p95":0.01377,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01108,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48795,-0.01219,0.15563]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2110.0,"contact_point_centroid":[0.52134,0.05706,0.2722],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52108,0.05706,0.26993]}],"total_contact_groups":11},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50408,-0.01389,0.02602],"final_tcp_position":[0.5747,0.16521,0.27057],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.44647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02593],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31229,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12241,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50241,-0.00298,0.22719],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02593],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31229,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":552.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.50214,-0.0122,0.07481],"tcp_start":[0.50241,-0.00298,0.22719],"tcp_to_object_dist_end":0.04894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50434,-0.00639,0.02308],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.30827,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.35129,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5590.0,"raw_peak_contact_force":0.37987,"tcp_end":[0.49108,-0.01223,0.06],"tcp_start":[0.50214,-0.0122,0.07481],"tcp_to_object_dist_end":0.03966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.50408,-0.01387,0.02602],"object_pos_start":[0.50434,-0.00639,0.02308],"object_to_goal_dist_end":0.311,"object_to_goal_dist_start":0.30827,"object_z_max":0.02988,"peak_contact_force":0.12287,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1782.0,"raw_peak_contact_force":0.44647,"subtask_id":"lift_clearance","tcp_end":[0.48827,-0.01219,0.19497],"tcp_start":[0.49108,-0.01223,0.06],"tcp_to_object_dist_end":0.1697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.50408,-0.01389,0.02602],"object_pos_start":[0.50408,-0.01387,0.02602],"object_to_goal_dist_end":0.31101,"object_to_goal_dist_start":0.311,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4090.0,"raw_peak_contact_force":0.123,"subtask_id":"place_goal","tcp_end":[0.5747,0.16521,0.27057],"tcp_start":[0.48827,-0.01219,0.19497],"tcp_to_object_dist_end":0.31124,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42601,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.06443,"lift_object.lift_height":0.20508,"transport_to_goal.arc_height":0.1447,"transport_to_goal.placement_z_offset":0.02044,"transport_to_goal.transport_speed":0.04221},"optimized_scores":{"best_composite_score":-0.02703,"best_fitness_score":0.31297,"best_task_score":0.24175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1257.0,"contact_point_centroid":[0.51291,0.03621,-0.00215],"force_p95":0.20722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45333,"mean_force":0.13045,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4956,0.03559,0.15245]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51271,0.03955,-0.00252],"force_p95":0.35834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37724,"mean_force":0.16704,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49973,0.03595,0.06064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.49907,0.04161,0.05569],"force_p95":0.18789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31942,"mean_force":0.09078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4974,0.03576,0.06076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50365,0.0244,0.05291],"force_p95":0.20166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25047,"mean_force":0.10116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49864,0.03586,0.05951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50151,0.02998,0.05443],"force_p95":0.20819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24829,"mean_force":0.11996,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4974,0.03576,0.06091]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.51251,0.03972,-0.00161],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1243,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50325,0.0141,0.27034]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.51287,0.0382,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55666,0.09975,0.24612]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12253,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50825,0.03262,0.15403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3154.0,"contact_point_centroid":[0.49891,0.04783,0.05476],"force_p95":0.07723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09985,"mean_force":0.04222,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49865,0.03586,0.05951]},{"body_a":"left_finger","body_b":"right_finger","contact_count":950.0,"contact_point_centroid":[0.49581,0.0356,0.17973],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01777,"mean_force":0.01078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49558,0.03559,0.17746]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1607.0,"contact_point_centroid":[0.55721,0.10003,0.24836],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01046,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55691,0.10001,0.24602]}],"total_contact_groups":11},"final_pose_error":0.02947,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51287,0.0382,0.02602],"final_tcp_position":[0.61746,0.16387,0.19176],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":85.52407,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02597],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":324.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50712,0.02888,0.22849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02597],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":85.52407,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":556.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.50971,0.03656,0.07469],"tcp_start":[0.50712,0.02888,0.22849],"tcp_to_object_dist_end":0.04886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51314,0.03086,0.02305],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21918,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.35547,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5754.0,"raw_peak_contact_force":0.37724,"tcp_end":[0.4986,0.03587,0.05946],"tcp_start":[0.50971,0.03656,0.07469],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.51287,0.03821,0.02602],"object_pos_start":[0.51314,0.03086,0.02305],"object_to_goal_dist_end":0.21297,"object_to_goal_dist_start":0.21918,"object_z_max":0.03051,"peak_contact_force":0.12265,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2454.0,"raw_peak_contact_force":0.45333,"subtask_id":"lift_clearance","tcp_end":[0.49608,0.03563,0.23507],"tcp_start":[0.4986,0.03587,0.05946],"tcp_to_object_dist_end":0.20974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.51287,0.0382,0.02602],"object_pos_start":[0.51287,0.03821,0.02602],"object_to_goal_dist_end":0.21298,"object_to_goal_dist_start":0.21297,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3115.0,"raw_peak_contact_force":0.12266,"subtask_id":"place_goal","tcp_end":[0.61746,0.16387,0.19176],"tcp_start":[0.49608,0.03563,0.23507],"tcp_to_object_dist_end":0.23281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44643,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07412,"lift_object.lift_height":0.15503,"transport_to_goal.arc_height":0.16527,"transport_to_goal.placement_z_offset":0.0334,"transport_to_goal.transport_speed":0.04144},"optimized_scores":{"best_composite_score":-0.07661,"best_fitness_score":0.26339,"best_task_score":0.14258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.4825,0.04238,-0.00226],"force_p95":0.2145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45208,"mean_force":0.13543,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47014,0.04359,0.1285]},{"body_a":"world","body_b":"grasp_target","contact_count":1653.0,"contact_point_centroid":[0.48109,0.0464,-0.00272],"force_p95":0.37119,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38908,"mean_force":0.17726,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47421,0.04403,0.06214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.47361,0.04766,0.05648],"force_p95":0.1997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35038,"mean_force":0.0922,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47207,0.04382,0.0619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":57.0,"contact_point_centroid":[0.47712,0.03995,0.05572],"force_p95":0.20066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20978,"mean_force":0.12492,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47189,0.0438,0.06229]},{"body_a":"world","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.4827,0.04873,-0.00162],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12428,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49616,0.01703,0.2694]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.48257,0.04527,-0.00199],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12314,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50616,0.1052,0.26445]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12253,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48726,0.03971,0.15387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":482.0,"contact_point_centroid":[0.47815,0.0397,0.05444],"force_p95":0.08084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11273,"mean_force":0.0491,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47306,0.04392,0.06101]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3139.0,"contact_point_centroid":[0.47272,0.05298,0.05583],"force_p95":0.06566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.075,"mean_force":0.03012,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4731,0.04392,0.06106]},{"body_a":"left_finger","body_b":"right_finger","contact_count":569.0,"contact_point_centroid":[0.47025,0.04359,0.15224],"force_p95":0.0138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.01118,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47004,0.04358,0.14992]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2057.0,"contact_point_centroid":[0.50668,0.10545,0.26706],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50629,0.10543,0.26478]}],"total_contact_groups":11},"final_pose_error":0.02999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48257,0.04527,0.02602],"final_tcp_position":[0.56704,0.20575,0.27594],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273020.11188,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02597],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.29001,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12212,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":328.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49035,0.03493,0.22721],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02597],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.29001,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":556.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.48373,0.04471,0.07484],"tcp_start":[0.49035,0.03493,0.22721],"tcp_to_object_dist_end":0.04899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48296,0.03731,0.02332],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29898,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.35551,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":5274.0,"raw_peak_contact_force":0.38908,"tcp_end":[0.47305,0.04392,0.06101],"tcp_start":[0.48373,0.04471,0.07484],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":244.0,"n_steps_budget":990.0,"object_pos_end":[0.48256,0.0452,0.02602],"object_pos_start":[0.48296,0.03731,0.02332],"object_to_goal_dist_end":0.29223,"object_to_goal_dist_start":0.29898,"object_z_max":0.02951,"peak_contact_force":0.12319,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1606.0,"raw_peak_contact_force":0.45208,"subtask_id":"lift_clearance","tcp_end":[0.47029,0.0436,0.18636],"tcp_start":[0.47305,0.04392,0.06101],"tcp_to_object_dist_end":0.16082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.48257,0.04527,0.02602],"object_pos_start":[0.48256,0.0452,0.02602],"object_to_goal_dist_end":0.29218,"object_to_goal_dist_start":0.29223,"object_z_max":0.02602,"peak_contact_force":273020.11188,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4001.0,"raw_peak_contact_force":0.12314,"subtask_id":"place_goal","tcp_end":[0.56704,0.20575,0.27594],"tcp_start":[0.47029,0.0436,0.18636],"tcp_to_object_dist_end":0.30878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```