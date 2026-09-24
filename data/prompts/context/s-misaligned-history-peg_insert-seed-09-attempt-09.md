## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 7  | 0.6881 | 0.90 | ❌ rejected |
| 8 | approach → align → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.6976 | 0.91 | ❌ rejected |
| 7 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.6040 | 0.91 | ❌ rejected |
| 6 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 7  | 0.7162 | 0.90 | ❌ rejected |
| 5 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.6388 | 0.90 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176062, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176062, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176062, -0.017054623272995572, 0.025)
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
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176062, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176062, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.911, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5296199363176062, -0.017054623272995572, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5296199363176062, -0.017054623272995572, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.639) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insertion
  anchor: fixture
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_to_entry
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.06
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_entry
- id: align_over_hole
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
    - 0.06
    tolerance: 0.003
    orientation:
      mode: keep_current
  parameters:
    align_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    align_y_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: approach_entry
- id: descend_into_hole
  type: descend
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 15.0
      - 40.0
      default: 35.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: add
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_entry** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.06], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **align_over_hole** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.06], tolerance=0.003
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_x_offset: status=consumed; consumers=target.offset.x (add)
    - align_y_offset: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **descend_into_hole** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (add)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.639
- **task_score** (E): 0.903
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_entry | 1.00 | 0.00 | 0.2130 |
| align_over_hole | 1.00 | 0.00 | 0.0121 |
| descend_into_hole | 1.00 | 1.00 | 0.0331 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.009, 0.090) | (0.504, -0.000, 0.340)→(0.509, -0.009, 0.130) | 0.260→0.059 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_over_hole | align | 1.00 / step_budget | (0.508, -0.009, 0.090)→(0.509, -0.008, 0.083) | (0.509, -0.009, 0.130)→(0.510, -0.008, 0.123) | 0.059→0.049 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_into_hole | descend | 1.00 / force_exceeded | (0.509, -0.008, 0.083)→(0.506, -0.009, 0.050) | (0.510, -0.008, 0.123)→(0.507, -0.009, 0.090) | 0.049→0.027 | 1.00 / 1.000 | 59.728 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.908
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.908
- phase_score: 0.578
- phase_breakdown.insertion_score: 0.499
- phase_breakdown.approach_entry_score: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.710
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.929
- **Median Q (composite search score)**: 0.651
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.352


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
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.976,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.03705,"align_over_hole.align_x_offset":-0.01581,"align_over_hole.align_y_offset":0.00784,"approach_to_entry.approach_speed":0.07091,"descend_into_hole.force_threshold":28.74187,"descend_into_hole.insert_depth":0.04472,"descend_into_hole.insert_speed":0.01569},"optimized_scores":{"best_composite_score":0.66329,"best_fitness_score":0.70995,"best_task_score":0.90799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.07126,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51741,-0.01305,0.05037],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":58.09276,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.52507,-0.01265,0.12937],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05679,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.52458,-0.01264,0.08937],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":43.0,"n_steps_budget":600.0,"object_pos_end":[0.51896,-0.01153,0.12468],"object_pos_start":[0.52507,-0.01265,0.12937],"object_to_goal_dist_end":0.04988,"object_to_goal_dist_start":0.05679,"object_z_max":0.12937,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.51819,-0.01152,0.08469],"tcp_start":[0.52458,-0.01264,0.08937],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.51865,-0.01307,0.09035],"object_pos_start":[0.51896,-0.01153,0.12468],"object_to_goal_dist_end":0.02501,"object_to_goal_dist_start":0.04988,"object_z_max":0.12468,"peak_contact_force":58.09276,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.51741,-0.01305,0.05037],"tcp_start":[0.51819,-0.01152,0.08469],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22078,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.01517,"align_over_hole.align_x_offset":-0.01275,"align_over_hole.align_y_offset":0.0128,"approach_to_entry.approach_speed":0.11496,"descend_into_hole.force_threshold":27.88476,"descend_into_hole.insert_depth":0.06223,"descend_into_hole.insert_speed":0.04426},"optimized_scores":{"best_composite_score":0.60261,"best_fitness_score":0.64928,"best_task_score":0.87253},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.08878,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52365,-0.01696,0.05038],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":58.09276,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.53169,-0.01885,0.12882],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06118,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.53121,-0.01884,0.08882],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":56.0,"n_steps_budget":600.0,"object_pos_end":[0.52579,-0.01511,0.12343],"object_pos_start":[0.53169,-0.01885,0.12882],"object_to_goal_dist_end":0.05272,"object_to_goal_dist_start":0.06118,"object_z_max":0.12882,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.52497,-0.01509,0.08343],"tcp_start":[0.53121,-0.01884,0.08882],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.52493,-0.01699,0.09036],"object_pos_start":[0.52579,-0.01511,0.12343],"object_to_goal_dist_end":0.0319,"object_to_goal_dist_start":0.05272,"object_z_max":0.12343,"peak_contact_force":58.09276,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.52365,-0.01696,0.05038],"tcp_start":[0.52497,-0.01509,0.08343],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`; realized-scene SHA-256: `6cd5caaafe0ec0cc23a4551cd60416799cdbf9885c1214f7b258fb3313892a60`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05495,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_hole.align_speed":0.03847,"align_over_hole.align_x_offset":0.01999,"align_over_hole.align_y_offset":0.00322,"approach_to_entry.approach_speed":0.11705,"descend_into_hole.force_threshold":34.02163,"descend_into_hole.insert_depth":0.0504,"descend_into_hole.insert_speed":0.02302},"optimized_scores":{"best_composite_score":0.6506,"best_fitness_score":0.69727,"best_task_score":0.92875},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.07623,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.47742,0.00228,0.05045],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":62.99791,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.46886,0.00376,0.13156],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06035,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.46843,0.00375,0.09156],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.48553,0.00316,0.12129],"object_pos_start":[0.46886,0.00376,0.13156],"object_to_goal_dist_end":0.04387,"object_to_goal_dist_start":0.06035,"object_z_max":0.13156,"peak_contact_force":0.0,"phase_name":"align_over_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.48467,0.00315,0.0813],"tcp_start":[0.46843,0.00375,0.09156],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.4787,0.00229,0.09043],"object_pos_start":[0.48553,0.00316,0.12129],"object_to_goal_dist_end":0.02383,"object_to_goal_dist_start":0.04387,"object_z_max":0.12129,"peak_contact_force":62.99791,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.47742,0.00228,0.05045],"tcp_start":[0.48467,0.00315,0.0813],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```