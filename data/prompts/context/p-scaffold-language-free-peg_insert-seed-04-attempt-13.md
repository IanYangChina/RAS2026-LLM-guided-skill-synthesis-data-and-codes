## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.4426 | 0.90 | ❌ rejected |
| 12 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 10 | 0.5895 | 0.90 | ❌ rejected |
| 11 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 10 | 0.5893 | 0.90 | ❌ rejected |
| 10 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 10 | 0.3876 | 0.90 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.4432 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457894, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457894, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457894, 0.000906204225148928, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457894, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457894, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.906, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, 0.000906204225148928, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5354444884457894, 0.000906204225148928, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.443) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_subtask
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insertion_subtask
  anchor: fixture
  weight: 0.7
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: approach_subtask
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_subtask
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - -0.02
    offset_along_axis:
      distance: 0.03
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_subtask
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    insertion_stroke:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_subtask
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
  retries:
    max_attempts: 1
    strategy: reduce_speed

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, -0.02], offset_along_axis={axis=channel_axis, distance=0.03, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.443
- **task_score** (E): 0.905
- **fitness_score**: 0.783  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1497 |
| approach_1 | 1.00 | 0.00 | 0.0730 |
| contact_1 | 1.00 | 1.00 | 0.0304 |
| insert_1 | 1.00 | 1.00 | 0.0065 |
| retract_1 | 0.33 | 0.00 | 0.0976 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.005, 0.153) | (0.504, -0.000, 0.340)→(0.519, 0.005, 0.193) | 0.260→0.116 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.519, 0.005, 0.153)→(0.517, 0.004, 0.080) | (0.519, 0.005, 0.193)→(0.517, 0.004, 0.120) | 0.116→0.048 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, 0.004, 0.080)→(0.514, 0.004, 0.050) | (0.517, 0.004, 0.120)→(0.515, 0.004, 0.090) | 0.048→0.026 | 1.00 / 1.000 | 65.919 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.514, 0.004, 0.050)→(0.521, 0.004, 0.050) | (0.515, 0.004, 0.090)→(0.521, 0.004, 0.090) | 0.026→0.030 | 1.00 / 1.000 | 432.245 | 479.162 |
| retract_1 | retract | 0.33 / step_budget | (0.521, 0.004, 0.050)→(0.518, 0.014, 0.147) | (0.521, 0.004, 0.090)→(0.518, 0.014, 0.187) | 0.030→0.111 | 0.00 / 0.000 | 0.000 | 50.756 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.992
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.992
- phase_score: 0.700
- phase_breakdown.approach_subtask_score: 0.919
- phase_breakdown.insertion_subtask_score: 0.606

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.817
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.992
- **Median Q (composite search score)**: 0.426
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.278


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9dafd9212fa57d4ed6b507cf5ac09991f034abfc2fa41dbd37d7c702246c6284`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ab22a59b7a3c9c0e28c9743e3882e986d7ba7a97654ba206ec4bffa38a24163`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12903,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00485,"align_1.lateral_offset_y":-0.00042,"approach_1.approach_height":0.04675,"contact_1.contact_force":10.47662,"contact_1.speed":0.02438,"insert_1.insertion_stroke":0.04978,"insert_1.speed":0.02595,"retract_1.retract_height":0.17351,"retract_1.speed":0.03835},"optimized_scores":{"best_composite_score":0.42602,"best_fitness_score":0.76602,"best_task_score":0.86288},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":310.0,"contact_point_centroid":[0.54697,0.00098,0.04995],"force_p95":432.50987,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.86548,"mean_force":415.2438,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53198,0.0007,0.05005]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.55097,0.00141,0.04997],"force_p95":50.00351,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.26434,"mean_force":44.1133,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53599,0.00071,0.05002]}],"total_contact_groups":2},"final_pose_error":0.06376,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53221,0.01463,0.13633],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":474.86548,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.53432,0.00041,0.19236],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11749,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.53384,0.00041,0.15236],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.53204,0.00076,0.12088],"object_pos_start":[0.53432,0.00041,0.19236],"object_to_goal_dist_end":0.05194,"object_to_goal_dist_start":0.11749,"object_z_max":0.19236,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.53157,0.00075,0.08088],"tcp_start":[0.53384,0.00041,0.15236],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.52903,0.00072,0.0901],"object_pos_start":[0.53204,0.00076,0.12088],"object_to_goal_dist_end":0.03074,"object_to_goal_dist_start":0.05194,"object_z_max":0.12088,"peak_contact_force":69.67267,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_subtask","tcp_end":[0.52855,0.00071,0.0501],"tcp_start":[0.53157,0.00075,0.08088],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.53616,0.00072,0.09002],"object_pos_start":[0.52903,0.00072,0.0901],"object_to_goal_dist_end":0.03753,"object_to_goal_dist_start":0.03074,"object_z_max":0.0901,"peak_contact_force":419.08095,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":310.0,"raw_peak_contact_force":474.86548,"subtask_id":"insertion_subtask","tcp_end":[0.53596,0.00071,0.05002],"tcp_start":[0.52855,0.00071,0.0501],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53288,0.01466,0.17632],"object_pos_start":[0.53616,0.00072,0.09002],"object_to_goal_dist_end":0.10283,"object_to_goal_dist_start":0.03753,"object_z_max":0.17625,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":51.26434,"tcp_end":[0.53221,0.01463,0.13633],"tcp_start":[0.53596,0.00071,0.05002],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1cd3bcde9ecee8889beeec63bba6949652ce08dd1277aacff8bc717cc59ca677`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12329,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00347,"align_1.lateral_offset_y":-0.00128,"approach_1.approach_height":0.04546,"contact_1.contact_force":5.49678,"contact_1.speed":0.02101,"insert_1.insertion_stroke":0.0431,"insert_1.speed":0.0132,"retract_1.retract_height":0.13694,"retract_1.speed":0.06274},"optimized_scores":{"best_composite_score":0.42493,"best_fitness_score":0.76493,"best_task_score":0.86004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":256.0,"contact_point_centroid":[0.53511,0.02626,0.04995],"force_p95":438.88409,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.44451,"mean_force":419.31791,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52037,0.02386,0.05005]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.53701,0.03098,0.04998],"force_p95":51.57812,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.99568,"mean_force":47.60483,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52376,0.02397,0.04999]}],"total_contact_groups":2},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52108,0.02596,0.15267],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":464.44451,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":486.0,"n_steps_budget":990.0,"object_pos_end":[0.52284,0.02125,0.19304],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11727,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.52237,0.02122,0.15305],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.52096,0.02387,0.11948],"object_pos_start":[0.52284,0.02125,0.19304],"object_to_goal_dist_end":0.05067,"object_to_goal_dist_start":0.11727,"object_z_max":0.19304,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.5205,0.02385,0.07948],"tcp_start":[0.52237,0.02122,0.15305],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.51799,0.02382,0.09011],"object_pos_start":[0.52096,0.02387,0.11948],"object_to_goal_dist_end":0.03152,"object_to_goal_dist_start":0.05067,"object_z_max":0.11948,"peak_contact_force":66.11238,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_subtask","tcp_end":[0.51752,0.0238,0.05011],"tcp_start":[0.5205,0.02385,0.07948],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":256.0,"n_steps_budget":720.0,"object_pos_end":[0.52382,0.02401,0.08997],"object_pos_start":[0.51799,0.02382,0.09011],"object_to_goal_dist_end":0.03526,"object_to_goal_dist_start":0.03152,"object_z_max":0.09012,"peak_contact_force":428.97872,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":256.0,"raw_peak_contact_force":464.44451,"subtask_id":"insertion_subtask","tcp_end":[0.52373,0.02397,0.04997],"tcp_start":[0.51752,0.0238,0.05011],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.52163,0.02603,0.19267],"object_pos_start":[0.52382,0.02401,0.08997],"object_to_goal_dist_end":0.11764,"object_to_goal_dist_start":0.03526,"object_z_max":0.19259,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":51.99568,"tcp_end":[0.52108,0.02596,0.15267],"tcp_start":[0.52373,0.02397,0.04997],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3a12d7f15d1e6c6a0af002631f15bc7a534f5434829fc9db32b3974b909f1f84`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20588,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00013,"align_1.lateral_offset_y":0.00578,"approach_1.approach_height":0.04677,"contact_1.contact_force":8.51694,"contact_1.speed":0.04037,"insert_1.insertion_stroke":0.04623,"insert_1.speed":0.02158,"retract_1.retract_height":0.17562,"retract_1.speed":0.05046},"optimized_scores":{"best_composite_score":0.47678,"best_fitness_score":0.81678,"best_task_score":0.99157},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":252.0,"contact_point_centroid":[0.51373,-0.01325,0.04994],"force_p95":462.43965,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.17653,"mean_force":441.39299,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49883,-0.01181,0.05003]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51695,-0.01466,0.04997],"force_p95":48.73914,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.00676,"mean_force":45.82973,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50225,-0.01188,0.05001]}],"total_contact_groups":2},"final_pose_error":0.0506,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49962,7e-05,0.15174],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":498.17653,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":454.0,"n_steps_budget":990.0,"object_pos_end":[0.50004,-0.00614,0.19434],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1145,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.49958,-0.00614,0.15434],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":241.0,"n_steps_budget":600.0,"object_pos_end":[0.49948,-0.01148,0.12063],"object_pos_start":[0.50004,-0.00614,0.19434],"object_to_goal_dist_end":0.04222,"object_to_goal_dist_start":0.1145,"object_z_max":0.19434,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_subtask","tcp_end":[0.49903,-0.01148,0.08063],"tcp_start":[0.49958,-0.00614,0.15434],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.49672,-0.01172,0.0901],"object_pos_start":[0.49948,-0.01148,0.12063],"object_to_goal_dist_end":0.01582,"object_to_goal_dist_start":0.04222,"object_z_max":0.12063,"peak_contact_force":61.97305,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_subtask","tcp_end":[0.49627,-0.01172,0.05011],"tcp_start":[0.49903,-0.01148,0.08063],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.50237,-0.01191,0.08999],"object_pos_start":[0.49672,-0.01172,0.0901],"object_to_goal_dist_end":0.01572,"object_to_goal_dist_start":0.01582,"object_z_max":0.0901,"peak_contact_force":448.6752,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":252.0,"raw_peak_contact_force":498.17653,"subtask_id":"insertion_subtask","tcp_end":[0.50222,-0.01188,0.04999],"tcp_start":[0.49627,-0.01172,0.05011],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50021,4e-05,0.19173],"object_pos_start":[0.50237,-0.01191,0.08999],"object_to_goal_dist_end":0.11173,"object_to_goal_dist_start":0.01572,"object_z_max":0.19165,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":49.00676,"tcp_end":[0.49962,7e-05,0.15174],"tcp_start":[0.50222,-0.01188,0.04999],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```