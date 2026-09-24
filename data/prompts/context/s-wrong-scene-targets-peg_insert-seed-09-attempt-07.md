## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.3970 | 0.91 | ✅ accepted |
| 6 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.4388 | 0.85 | ❌ rejected |
| 5 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.4539 | 0.30 | ❌ rejected |
| 4 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | -0.1517 | 0.11 | ❌ rejected |
| 3 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.4386 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`
- Frozen object start: [0.5296199363176062, -0.017054623272995572, 0.08]
- Frozen task target: [0.5296199363176062, -0.017054623272995572, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5296199363176062, -0.017054623272995572, 0.08)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
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
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5296199363176062, -0.017054623272995572, 0.08]}
  frozen_targets: {'socket_entry': [0.5296199363176062, -0.017054623272995572, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.913, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5296199363176062, -0.017054623272995572, 0.08) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.3) | approach/contact targets near fixture |

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

## Current Skill (Q=0.397) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.3
- id: insert_peg
  offset:
  - 0.0
  - 0.0
  - -0.055
  weight: 0.7
phases:
- id: approach_socket
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
    - 0.005
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    approach_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_socket
- id: insert_peg
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.003
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: insert_force
    when: during_phase
    predicate: force_below
    threshold: 39.9
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (replace)
    - approach_offset_y: status=consumed; consumers=target.offset.y (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **insert_peg** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.003
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insert_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=39.9
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.397
- **task_score** (E): 0.913
- **fitness_score**: 0.647  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_socket | 1.00 | 0.00 | 0.2123 |
| insert_peg | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.006, 0.089) | (0.504, -0.000, 0.340)→(0.515, -0.006, 0.129) | 0.260→0.054 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_peg | insert | 0.00 / guard_failure | (0.507, -0.006, 0.050)→(0.507, -0.006, 0.050) | (0.515, -0.006, 0.129)→(0.507, -0.006, 0.090) | 0.054→0.022 | 1.00 / 1.000 | 43.415 | 47.311 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.928
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.928
- phase_score: 0.480
- phase_breakdown.insert_peg_score: 0.546
- phase_breakdown.approach_socket_score: 0.325

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.659
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.928
- **Median Q (composite search score)**: 0.406
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.01705,0.08]},{"name":"task_object","value":[0.52962,-0.01705,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.52962,-0.01705,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69492,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_offset_x":-0.0057,"approach_socket.approach_offset_y":0.00886,"approach_socket.approach_speed":0.16562,"insert_peg.insert_depth":0.04129,"insert_peg.insert_speed":0.02891},"optimized_scores":{"best_composite_score":0.40606,"best_fitness_score":0.65606,"best_task_score":0.92111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.53002,-0.00797,0.04994],"force_p95":43.70011,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.07563,"mean_force":32.70202,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51503,-0.00784,0.05005]}],"total_contact_groups":1},"final_pose_error":0.00417,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51503,-0.00784,0.04994],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":45.07563,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":798.0,"n_steps_budget":840.0,"object_pos_end":[0.52361,-0.00783,0.12974],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05561,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.51901,-0.00783,0.09],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":900.0,"object_pos_end":[0.5155,-0.00784,0.09002],"object_pos_start":[0.52361,-0.00783,0.12974],"object_to_goal_dist_end":0.02005,"object_to_goal_dist_start":0.05561,"object_z_max":0.12974,"peak_contact_force":40.49057,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":45.07563,"subtask_id":"insert_peg","tcp_end":[0.51503,-0.00784,0.04994],"tcp_start":[0.51503,-0.00784,0.04996],"tcp_to_object_dist_end":0.04008,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,-0.02339,0.08]},{"name":"task_object","value":[0.53648,-0.02339,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.53648,-0.02339,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92982,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_offset_x":-0.00567,"approach_socket.approach_offset_y":0.01396,"approach_socket.approach_speed":0.15549,"insert_peg.insert_depth":0.05866,"insert_peg.insert_speed":0.03319},"optimized_scores":{"best_composite_score":0.37584,"best_fitness_score":0.62584,"best_task_score":0.89091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.5366,-0.00908,0.04992],"force_p95":42.56724,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.34258,"mean_force":32.39817,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52161,-0.00903,0.05002]}],"total_contact_groups":1},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52161,-0.00903,0.0499],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":44.34258,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":856.0,"n_steps_budget":900.0,"object_pos_end":[0.53024,-0.00903,0.12892],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05822,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.52564,-0.00903,0.08919],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.52208,-0.00903,0.08999],"object_pos_start":[0.53024,-0.00903,0.12892],"object_to_goal_dist_end":0.02586,"object_to_goal_dist_start":0.05822,"object_z_max":0.12892,"peak_contact_force":37.24121,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":44.34258,"subtask_id":"insert_peg","tcp_end":[0.52161,-0.00903,0.0499],"tcp_start":[0.52161,-0.00903,0.04992],"tcp_to_object_dist_end":0.0401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`; realized-scene SHA-256: `6cd5caaafe0ec0cc23a4551cd60416799cdbf9885c1214f7b258fb3313892a60`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,-6e-05,0.08]},{"name":"task_object","value":[0.47029,-6e-05,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.47029,-6e-05,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91358,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_offset_x":0.01981,"approach_socket.approach_offset_y":-0.00106,"approach_socket.approach_speed":0.12142,"insert_peg.insert_depth":0.04161,"insert_peg.insert_speed":0.01887},"optimized_scores":{"best_composite_score":0.40915,"best_fitness_score":0.65915,"best_task_score":0.92799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.49803,-0.00084,0.04995],"force_p95":49.52386,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.51342,"mean_force":34.49169,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48304,-0.00117,0.05006]}],"total_contact_groups":1},"final_pose_error":0.00471,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.48303,-0.00117,0.04997],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":52.51342,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.49137,-0.00112,0.12849],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04927,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.4868,-0.00112,0.08875],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.48348,-0.00117,0.09003],"object_pos_start":[0.49137,-0.00112,0.12849],"object_to_goal_dist_end":0.01936,"object_to_goal_dist_start":0.04927,"object_z_max":0.12849,"peak_contact_force":52.51342,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":9.0,"raw_peak_contact_force":52.51342,"subtask_id":"insert_peg","tcp_end":[0.48303,-0.00117,0.04997],"tcp_start":[0.48304,-0.00117,0.04999],"tcp_to_object_dist_end":0.04006,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```