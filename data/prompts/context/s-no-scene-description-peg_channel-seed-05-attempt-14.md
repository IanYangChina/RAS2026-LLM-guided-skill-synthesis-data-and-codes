## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | rotate → release → approach → descend → grasp → approach → descend → push | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1487 | 0.36 | ✅ accepted |
| 13 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0984 | 0.00 | ❌ rejected |
| 12 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | time_limit | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1062 | 0.00 | ❌ rejected |
| 11 | grasp → lift → rotate → approach → descend → push → retract | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1583 | 0.04 | ❌ rejected |
| 10 | approach → grasp → lift → rotate → approach → descend → push → retract | linear_cartesian | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2305 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=-0.149) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insert_through_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: rotate_to_horizontal
  type: rotate
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    rotation_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: open_gripper
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
- id: approach_peg_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed_peg:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
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
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: grasp_peg
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
- id: approach_channel_entry_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed_channel:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_channel_entry
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: insert
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_force_threshold:
      type: scalar
      range:
      - 20.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.insert_force_guard.threshold
        mode: replace
  guards:
  - id: insert_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.005
  subtask_id: insert_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rotate_to_horizontal** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - rotation_speed: status=consumed; consumers=generator.speed (replace)
- **open_gripper** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **approach_peg_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed_peg: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_peg** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **approach_channel_entry_above** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed_channel: status=consumed; consumers=generator.speed (replace)
- **descend_to_channel_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **insert** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_force_threshold: status=consumed; consumers=guards.insert_force_guard.threshold (replace)
  - guards:
    - id=insert_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.005]

## Design Metrics

- **Composite score**: -0.149
- **task_score** (E): 0.360
- **fitness_score**: 0.281  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_to_horizontal | 1.00 | 1.00 | 0.0096 |
| open_gripper | 1.00 | 1.00 | 0.0093 |
| approach_peg_above | 1.00 | 1.00 | 0.1717 |
| descend_to_peg | 1.00 | 1.00 | 0.0795 |
| grasp_peg | 1.00 | 1.00 | 0.0032 |
| approach_channel_entry_above | 1.00 | 1.00 | 0.0681 |
| descend_to_channel_entry | 1.00 | 1.00 | 0.0663 |
| insert | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_to_horizontal | rotate | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.539 | 2.488 |
| open_gripper | release | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.495, 0.197, 0.282) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.562 | 0.587 |
| approach_peg_above | approach | 1.00 / step_budget | (0.495, 0.197, 0.282)→(0.501, 0.101, 0.140) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.552 | 0.589 |
| descend_to_peg | descend | 1.00 / step_budget | (0.501, 0.101, 0.140)→(0.501, 0.093, 0.062) | (0.504, 0.095, 0.034)→(0.504, 0.084, 0.033) | 0.175→0.165 | 1.00 / 1.667 | 79.933 | 209.338 |
| grasp_peg | grasp | 1.00 / step_budget | (0.501, 0.093, 0.062)→(0.502, 0.092, 0.064) | (0.504, 0.084, 0.033)→(0.507, 0.036, 0.030) | 0.165→0.119 | 1.00 / 3.000 | 77.399 | 99.457 |
| approach_channel_entry_above | approach | 1.00 / step_budget | (0.502, 0.092, 0.064)→(0.498, 0.080, 0.130) | (0.507, 0.036, 0.030)→(0.506, 0.035, 0.031) | 0.119→0.118 | 1.00 / 1.000 | 0.559 | 75.059 |
| descend_to_channel_entry | descend | 1.00 / step_budget | (0.498, 0.080, 0.130)→(0.503, 0.085, 0.064) | (0.506, 0.035, 0.031)→(0.507, 0.033, 0.029) | 0.118→0.116 | 1.00 / 3.333 | 273.882 | 484.475 |
| insert | push | 0.00 / guard_failure | (0.503, 0.085, 0.064)→(0.503, 0.086, 0.064) | (0.507, 0.033, 0.029)→(0.507, 0.033, 0.029) | 0.116→0.116 | 1.00 / 3.000 | 39.189 | 78.349 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.825
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.825
- phase_score: 0.253
- phase_breakdown.insert_through_channel_score: 0.000
- phase_breakdown.approach_peg_score: 0.845

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.482
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.825
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0206
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.329


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16312,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel_entry_above.approach_speed_channel":0.03407,"approach_peg_above.approach_speed_peg":0.12201,"insert.insert_distance":0.10643,"insert.insert_force_threshold":33.14759,"rotate_to_horizontal.rotation_speed":0.1276},"optimized_scores":{"best_composite_score":-0.27554,"best_fitness_score":0.15446,"best_task_score":0.09966},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":99.0,"contact_point_centroid":[0.50887,0.27363,-0.00013],"force_p95":423.83339,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.79619,"mean_force":332.25447,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.50256,0.0853,0.06648]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":91.0,"contact_point_centroid":[0.52501,0.11998,0.05461],"force_p95":168.41222,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.23229,"mean_force":113.00454,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49768,0.08254,0.08061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":375.0,"contact_point_centroid":[0.50492,0.10637,0.00853],"force_p95":135.78922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.57276,"mean_force":47.93854,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5023,0.1053,0.08813]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50257,0.09536,0.05542],"force_p95":142.66816,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.3411,"mean_force":94.16651,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.50151,0.08493,0.0672]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.50382,0.11325,0.0526],"force_p95":140.04911,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.87001,"mean_force":113.47729,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50338,0.10179,0.06316]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50657,0.08525,0.00905],"force_p95":104.69204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.45547,"mean_force":38.1416,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49884,0.08236,0.08655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.5043,0.10131,0.0084],"force_p95":103.56076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.30037,"mean_force":81.97956,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50217,0.09359,0.06709]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50321,0.10534,0.05516],"force_p95":102.58712,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.75358,"mean_force":80.97061,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50217,0.09359,0.06709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":626.0,"contact_point_centroid":[0.50524,0.07955,0.00939],"force_p95":7.99455,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.61924,"mean_force":1.91302,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49856,0.08548,0.09881]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.51385,0.27489,-0.00013],"force_p95":57.21931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.11689,"mean_force":43.67054,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50631,0.08657,0.06637]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.50207,0.09773,0.05785],"force_p95":49.06202,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.62366,"mean_force":15.737,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.50126,0.09231,0.06982]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":120.0,"contact_point_centroid":[0.52555,0.07814,0.02925],"force_p95":34.70143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.22682,"mean_force":14.73775,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.50225,0.08519,0.06659]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50745,0.0764,0.00849],"force_p95":51.95097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.04806,"mean_force":50.41827,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50631,0.08657,0.06637]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.507,0.09494,0.05507],"force_p95":51.34175,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.78273,"mean_force":48.79055,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50631,0.08657,0.06637]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":418.0,"contact_point_centroid":[0.5251,0.08741,0.01596],"force_p95":10.17765,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.11716,"mean_force":2.90175,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50224,0.09353,0.06723]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52504,0.10348,0.03064],"force_p95":11.03931,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.39488,"mean_force":4.07057,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50445,0.10384,0.06122]}],"total_contact_groups":22},"final_pose_error":0.11624,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50855,0.07721,0.032],"final_tcp_position":[0.50639,0.08658,0.06643],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":496.79619,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55385,"phase_name":"rotate_to_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":224.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49739,0.19833,0.29115],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.55111,"phase_name":"open_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.57958,"tcp_end":[0.49536,0.19673,0.28225],"tcp_start":[0.49739,0.19833,0.29115],"tcp_to_object_dist_end":0.26517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":500.0,"n_steps_budget":900.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.52966,"phase_name":"approach_peg_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":0.57724,"subtask_id":"approach_peg","tcp_end":[0.50265,0.11078,0.14088],"tcp_start":[0.49536,0.19673,0.28225],"tcp_to_object_dist_end":0.10726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":375.0,"n_steps_budget":690.0,"object_pos_end":[0.5066,0.09588,0.02974],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.17631,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":123.19399,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":570.0,"raw_peak_contact_force":155.57276,"tcp_end":[0.50126,0.09501,0.06401],"tcp_start":[0.50265,0.11078,0.14088],"tcp_to_object_dist_end":0.0347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50732,0.08155,0.03225],"object_pos_start":[0.5066,0.09588,0.02974],"object_to_goal_dist_end":0.1619,"object_to_goal_dist_start":0.17631,"object_z_max":0.03227,"peak_contact_force":79.18239,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1318.0,"raw_peak_contact_force":107.30037,"tcp_end":[0.50214,0.09326,0.06711],"tcp_start":[0.50126,0.09501,0.06401],"tcp_to_object_dist_end":0.03714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.50628,0.07998,0.03379],"object_pos_start":[0.50732,0.08155,0.03225],"object_to_goal_dist_end":0.16023,"object_to_goal_dist_start":0.1619,"object_z_max":0.03485,"peak_contact_force":0.54085,"phase_name":"approach_channel_entry_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":689.0,"raw_peak_contact_force":61.61924,"tcp_end":[0.49758,0.07965,0.13034],"tcp_start":[0.50214,0.09326,0.06711],"tcp_to_object_dist_end":0.09694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":600.0,"object_pos_end":[0.50863,0.07732,0.03199],"object_pos_start":[0.50628,0.07998,0.03379],"object_to_goal_dist_end":0.15775,"object_to_goal_dist_start":0.16023,"object_z_max":0.03379,"peak_contact_force":317.43667,"phase_name":"descend_to_channel_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":813.0,"raw_peak_contact_force":496.79619,"tcp_end":[0.50626,0.08657,0.06634],"tcp_start":[0.49758,0.07965,0.13034],"tcp_to_object_dist_end":0.03566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":750.0,"object_pos_end":[0.5086,0.07728,0.03199],"object_pos_start":[0.50863,0.07732,0.03199],"object_to_goal_dist_end":0.15772,"object_to_goal_dist_start":0.15775,"object_z_max":0.032,"peak_contact_force":48.12967,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":59.11689,"subtask_id":"insert_through_channel","tcp_end":[0.50639,0.08658,0.06643],"tcp_start":[0.50635,0.08657,0.0664],"tcp_to_object_dist_end":0.03574,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41129,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel_entry_above.approach_speed_channel":0.1462,"approach_peg_above.approach_speed_peg":0.10818,"insert.insert_distance":0.16597,"insert.insert_force_threshold":31.05566,"rotate_to_horizontal.rotation_speed":0.11307},"optimized_scores":{"best_composite_score":0.05204,"best_fitness_score":0.48204,"best_task_score":0.82489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.49673,0.14064,-0.00041],"force_p95":335.59117,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":457.36019,"mean_force":254.2224,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49748,0.08195,0.05707]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.52502,0.11995,0.05876],"force_p95":306.46281,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.77831,"mean_force":254.82547,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50094,0.07918,0.082]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.47499,0.11997,0.05293],"force_p95":143.10142,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.74156,"mean_force":106.94802,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49766,0.08001,0.07666]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.47495,0.11989,0.05993],"force_p95":188.86934,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.04314,"mean_force":121.15071,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49933,0.07199,0.09062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50321,0.06729,0.00935],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.65659,"mean_force":3.96982,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50027,0.07706,0.09285]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50247,0.08412,0.05513],"force_p95":171.9796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.52135,"mean_force":86.64947,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5023,0.08132,0.06644]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50223,0.14088,-2e-05],"force_p95":102.75341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.33501,"mean_force":72.50967,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.50245,0.08065,0.05627]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.475,0.12,0.05144],"force_p95":49.91806,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.80541,"mean_force":33.03073,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49879,0.08062,0.07152]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.525,0.12,0.03856],"force_p95":39.68564,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.68339,"mean_force":25.0719,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.50106,0.08058,0.059]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49706,0.14071,-0.00014],"force_p95":93.83994,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.43983,"mean_force":81.4393,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.49711,0.08353,0.05914]},{"body_a":"world","body_b":"link7","contact_count":430.0,"contact_point_centroid":[0.50216,0.14094,-3e-05],"force_p95":78.72422,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.61252,"mean_force":71.56729,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50238,0.08067,0.05622]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.525,0.12,0.03449],"force_p95":28.89615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.18466,"mean_force":8.8595,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50257,0.08063,0.05636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50235,-0.0573,0.00832],"force_p95":1.1815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17765,"mean_force":0.67643,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.5024,0.08068,0.05625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50637,-0.06488,0.00814],"force_p95":0.73766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08918,"mean_force":0.61782,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49854,0.07972,0.09167]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,-0.08865,0.02425],"force_p95":8.70832,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.71054,"mean_force":2.76888,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50242,0.08067,0.05627]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,-0.08895,0.02427],"force_p95":8.26581,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.68076,"mean_force":4.53131,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49763,0.07884,0.12865]}],"total_contact_groups":23},"final_pose_error":0.17065,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50439,-0.06452,0.02415],"final_tcp_position":[0.49717,0.08358,0.05917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":457.36019,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06749,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5503,"phase_name":"rotate_to_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":203.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49739,0.19833,0.29115],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50301,0.06749,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14765,"object_z_max":0.0338,"peak_contact_force":0.54456,"phase_name":"open_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.56003,"tcp_end":[0.49536,0.19673,0.28225],"tcp_start":[0.49739,0.19833,0.29115],"tcp_to_object_dist_end":0.28017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54568,"phase_name":"approach_peg_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":0.55115,"subtask_id":"approach_peg","tcp_end":[0.50008,0.07531,0.13927],"tcp_start":[0.49536,0.19673,0.28225],"tcp_to_object_dist_end":0.1058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":690.0,"object_pos_end":[0.50216,0.05239,0.03967],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.13241,"object_to_goal_dist_start":0.14766,"object_z_max":0.03906,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":766.0,"raw_peak_contact_force":313.77831,"tcp_end":[0.50343,0.08065,0.05807],"tcp_start":[0.50008,0.07531,0.13927],"tcp_to_object_dist_end":0.03374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50636,-0.06435,0.02438],"object_pos_start":[0.50216,0.05239,0.03967],"object_to_goal_dist_end":0.02301,"object_to_goal_dist_start":0.13241,"object_z_max":0.0442,"peak_contact_force":72.18754,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":899.0,"raw_peak_contact_force":81.61252,"tcp_end":[0.50245,0.08065,0.05627],"tcp_start":[0.50343,0.08065,0.05807],"tcp_to_object_dist_end":0.14852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50644,-0.06451,0.02443],"object_pos_start":[0.50636,-0.06435,0.02438],"object_to_goal_dist_end":0.02288,"object_to_goal_dist_start":0.02301,"object_z_max":0.02442,"peak_contact_force":0.6008,"phase_name":"approach_channel_entry_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":620.0,"raw_peak_contact_force":107.33501,"tcp_end":[0.49763,0.07885,0.12937],"tcp_start":[0.50245,0.08065,0.05627],"tcp_to_object_dist_end":0.17788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":306.0,"n_steps_budget":600.0,"object_pos_end":[0.50441,-0.06453,0.02416],"object_pos_start":[0.50644,-0.06451,0.02443],"object_to_goal_dist_end":0.02258,"object_to_goal_dist_start":0.02288,"object_z_max":0.02449,"peak_contact_force":242.5971,"phase_name":"descend_to_channel_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":418.0,"raw_peak_contact_force":457.36019,"tcp_end":[0.49708,0.0835,0.05911],"tcp_start":[0.49763,0.07885,0.12937],"tcp_to_object_dist_end":0.15228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5044,-0.0645,0.02415],"object_pos_start":[0.50441,-0.06453,0.02416],"object_to_goal_dist_end":0.0226,"object_to_goal_dist_start":0.02258,"object_z_max":0.02416,"peak_contact_force":69.4372,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":95.43983,"subtask_id":"insert_through_channel","tcp_end":[0.49717,0.08358,0.05917],"tcp_start":[0.49713,0.08356,0.05916],"tcp_to_object_dist_end":0.15233,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08966,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel_entry_above.approach_speed_channel":0.19195,"approach_peg_above.approach_speed_peg":0.05911,"insert.insert_distance":0.19384,"insert.insert_force_threshold":29.01299,"rotate_to_horizontal.rotation_speed":0.08941},"optimized_scores":{"best_composite_score":-0.22273,"best_fitness_score":0.20727,"best_task_score":0.15669},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.509,0.27316,-0.00014],"force_p95":430.33338,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":499.26815,"mean_force":321.87581,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.5024,0.08513,0.06728]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":92.0,"contact_point_centroid":[0.52501,0.11998,0.05348],"force_p95":168.47942,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.99536,"mean_force":105.37812,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49773,0.08271,0.07886]},{"body_a":"attachment","body_b":"peg","contact_count":154.0,"contact_point_centroid":[0.50274,0.10524,0.05501],"force_p95":147.77916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.38207,"mean_force":102.14819,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.50116,0.08472,0.0681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":375.0,"contact_point_centroid":[0.50285,0.1135,0.0085],"force_p95":137.23993,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.66442,"mean_force":49.10676,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50035,0.1124,0.08799]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.5019,0.12045,0.05221],"force_p95":142.2158,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.98814,"mean_force":115.98463,"phase_index":3.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50153,0.10933,0.06259]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.50672,0.09541,0.00897],"force_p95":113.8887,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.76473,"mean_force":43.8629,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.49868,0.08243,0.08657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.5025,0.11128,0.00841],"force_p95":104.39104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.45774,"mean_force":82.33764,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50027,0.10132,0.06731]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50145,0.11501,0.05517],"force_p95":103.88499,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.88283,"mean_force":81.77388,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50027,0.10132,0.06731]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.51371,0.27441,-3e-05],"force_p95":76.13893,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.49154,"mean_force":44.03182,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50597,0.08636,0.06732]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50726,0.1045,0.05468],"force_p95":64.16517,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.99693,"mean_force":56.50507,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50597,0.08636,0.06732]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50052,0.10003,0.00833],"force_p95":62.66041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.28532,"mean_force":55.35393,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50597,0.08636,0.06732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":137.0,"contact_point_centroid":[0.5255,0.08813,0.02987],"force_p95":30.50844,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.44517,"mean_force":13.35582,"phase_index":6.0,"phase_name":"descend_to_channel_entry","phase_type":"descend","tcp_position_centroid":[0.50158,0.08485,0.0676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.50529,0.08889,0.0094],"force_p95":9.75098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.22319,"mean_force":2.03027,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49765,0.08957,0.09855]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.50049,0.10707,0.05811],"force_p95":40.00253,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.81214,"mean_force":14.0374,"phase_index":5.0,"phase_name":"approach_channel_entry_above","phase_type":"approach","tcp_position_centroid":[0.49937,0.09959,0.07036]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52591,0.08679,0.02557],"force_p95":13.10315,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.39779,"mean_force":10.84482,"phase_index":7.0,"phase_name":"insert","phase_type":"push","tcp_position_centroid":[0.50597,0.08636,0.06732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52507,0.09298,0.01537],"force_p95":7.18445,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.87839,"mean_force":2.57328,"phase_index":4.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50026,0.10104,0.06738]}],"total_contact_groups":21},"final_pose_error":0.20214,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50876,0.08671,0.03174],"final_tcp_position":[0.50607,0.08635,0.06739],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":499.26815,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.50369,0.11179,0.03387],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51346,"phase_name":"rotate_to_horizontal","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":213.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49739,0.19833,0.29115],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,0.11176,0.03381],"object_pos_start":[0.50369,0.11179,0.03387],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19192,"object_z_max":0.03393,"peak_contact_force":0.58979,"phase_name":"open_gripper","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.62002,"tcp_end":[0.49536,0.19673,0.28225],"tcp_start":[0.49739,0.19833,0.29115],"tcp_to_object_dist_end":0.26271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03389],"object_pos_start":[0.50376,0.11176,0.03381],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.1919,"object_z_max":0.03392,"peak_contact_force":0.58025,"phase_name":"approach_peg_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":0.63808,"subtask_id":"approach_peg","tcp_end":[0.50067,0.11746,0.1411],"tcp_start":[0.49536,0.19673,0.28225],"tcp_to_object_dist_end":0.1074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":375.0,"n_steps_budget":690.0,"object_pos_end":[0.50442,0.10498,0.02949],"object_pos_start":[0.50371,0.11177,0.03389],"object_to_goal_dist_end":0.18533,"object_to_goal_dist_start":0.1919,"object_z_max":0.03389,"peak_contact_force":116.60446,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":532.0,"raw_peak_contact_force":158.66442,"tcp_end":[0.49935,0.10269,0.06384],"tcp_start":[0.50067,0.11746,0.1411],"tcp_to_object_dist_end":0.0348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5073,0.09178,0.03223],"object_pos_start":[0.50442,0.10498,0.02949],"object_to_goal_dist_end":0.17211,"object_to_goal_dist_start":0.18533,"object_z_max":0.03222,"peak_contact_force":80.82848,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":992.0,"raw_peak_contact_force":109.45774,"tcp_end":[0.50018,0.101,0.06729],"tcp_start":[0.49935,0.10269,0.06384],"tcp_to_object_dist_end":0.03695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.50656,0.09,0.03377],"object_pos_start":[0.5073,0.09178,0.03223],"object_to_goal_dist_end":0.17024,"object_to_goal_dist_start":0.17211,"object_z_max":0.03513,"peak_contact_force":0.53424,"phase_name":"approach_channel_entry_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":555.0,"raw_peak_contact_force":56.22319,"tcp_end":[0.49749,0.08025,0.13007],"tcp_start":[0.50018,0.101,0.06729],"tcp_to_object_dist_end":0.09722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":600.0,"object_pos_end":[0.50879,0.08682,0.03171],"object_pos_start":[0.50656,0.09,0.03377],"object_to_goal_dist_end":0.16726,"object_to_goal_dist_start":0.17024,"object_z_max":0.03378,"peak_contact_force":261.61258,"phase_name":"descend_to_channel_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":834.0,"raw_peak_contact_force":499.26815,"tcp_end":[0.50591,0.08637,0.06729],"tcp_start":[0.49749,0.08025,0.13007],"tcp_to_object_dist_end":0.03569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50878,0.08678,0.03172],"object_pos_start":[0.50879,0.08682,0.03171],"object_to_goal_dist_end":0.16722,"object_to_goal_dist_start":0.16726,"object_z_max":0.03172,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":80.49154,"subtask_id":"insert_through_channel","tcp_end":[0.50607,0.08635,0.06739],"tcp_start":[0.50602,0.08635,0.06735],"tcp_to_object_dist_end":0.03578,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```