## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0958 | 0.32 | ❌ rejected |
| 11 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0627 | 0.32 | ❌ rejected |
| 10 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0851 | 0.34 | ❌ rejected |
| 9 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0597 | 0.31 | ❌ rejected |
| 8 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0898 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.096) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  weight: 0.7
phases:
- id: approach_above
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
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
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
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: grasp_object
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
  parameters:
    max_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
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
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
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
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: approach_goal
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
    - 0.25
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: descend_to_goal
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.096
- **task_score** (E): 0.324
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1116 |
| descend_to_grasp | 1.00 | 1.00 | 0.1468 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1708 |
| transport_to_goal | 0.67 | 1.00 | 0.0859 |
| descend_to_place | 1.00 | 1.00 | 0.1926 |
| release_object | 1.00 | 1.00 | 0.0102 |
| retract_from_place | 1.00 | 1.00 | 0.0755 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.193) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.193)→(0.492, 0.001, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.047)→(0.484, 0.000, 0.038) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.333 | 0.143 | 0.197 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.038)→(0.481, 0.000, 0.209) | (0.497, 0.001, 0.026)→(0.490, 0.000, 0.193) | 0.266→0.213 | 1.00 / 40.000 | 0.052 | 0.461 |
| transport_to_goal | approach | 0.67 / step_budget | (0.523, 0.117, 0.337)→(0.563, 0.163, 0.398) | (0.490, 0.000, 0.193)→(0.563, 0.152, 0.117) | 0.213→0.163 | 1.00 / 11.333 | 3249.786 | 1.783 |
| descend_to_place | approach | 1.00 / step_budget | (0.563, 0.163, 0.398)→(0.579, 0.182, 0.211) | (0.563, 0.152, 0.117)→(0.573, 0.180, 0.016) | 0.163→0.172 | 1.00 / 8.667 | 91002.708 | 0.769 |
| release_object | release | 1.00 / step_budget | (0.574, 0.180, 0.231)→(0.574, 0.181, 0.242) | (0.573, 0.180, 0.016)→(0.572, 0.180, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.127 |
| retract_from_place | retract | 1.00 / step_budget | (0.574, 0.181, 0.242)→(0.580, 0.184, 0.317) | (0.572, 0.180, 0.016)→(0.572, 0.180, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.417
- phase_score: 0.595
- phase_breakdown.reach_object_score: 0.070
- phase_breakdown.place_goal_score: 0.820
- grasp_place_fitness: 0.680

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.680
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.417
- **Median Q (composite search score)**: -0.105
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.379


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43581,"average_solve_count":296.0,"average_success_count":296.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.12747,"descend_to_grasp.descend_offset":0.01173,"descend_to_grasp.speed":0.18051,"descend_to_place.place_z_offset":0.02721,"descend_to_place.speed":0.06177,"grasp_object.max_duration":0.56604,"lift_object.lift_height":0.22131,"lift_object.speed":0.02028,"release_object.release_duration":0.73742,"retract_from_place.speed":0.23738,"transport_to_goal.speed":0.22832},"optimized_scores":{"best_composite_score":-0.13262,"best_fitness_score":0.59738,"best_task_score":0.24934},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1466.0,"contact_point_centroid":[0.54761,0.12089,-0.00322],"force_p95":0.3993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.69845,"mean_force":0.17246,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54413,0.12278,0.42656]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50961,-0.02209,-0.00151],"force_p95":0.44283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.466,"mean_force":0.19375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49932,-0.02236,0.0379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6995.0,"contact_point_centroid":[0.51225,3e-05,0.29036],"force_p95":0.13198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30638,"mean_force":0.07867,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50887,0.0189,0.28892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13748.0,"contact_point_centroid":[0.49697,-0.00314,0.13709],"force_p95":0.07717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27851,"mean_force":0.0535,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49686,-0.02228,0.13473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8309.0,"contact_point_centroid":[0.51338,0.03975,0.29281],"force_p95":0.10201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27327,"mean_force":0.06794,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50962,0.02115,0.29188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14262.0,"contact_point_centroid":[0.49691,-0.04139,0.1356],"force_p95":0.07576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26317,"mean_force":0.05212,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49685,-0.02228,0.1336]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00206],"force_p95":0.14009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18204,"mean_force":0.12736,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50159,-0.02241,0.03833]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50339,-0.00923,0.24754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.50099,-0.00318,0.03981],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12956,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50042,-0.02239,0.03705]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50725,-0.02091,0.11878]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.54717,0.12111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55197,0.14864,0.35894]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.54717,0.12111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54806,0.14948,0.2653]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.54717,0.12111,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54858,0.14976,0.32039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.50104,-0.04148,0.03888],"force_p95":0.06986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08126,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50042,-0.02239,0.03706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1544.0,"contact_point_centroid":[0.54454,0.12312,0.42925],"force_p95":0.01151,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.01067,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54424,0.12312,0.427]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2431.0,"contact_point_centroid":[0.55236,0.14865,0.36159],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55198,0.14863,0.35935]}],"total_contact_groups":17},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54717,0.12111,0.01602],"final_tcp_position":[0.55142,0.1507,0.35231],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9749.08068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5084,-0.01932,0.19314],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5086,-0.02257,0.04609],"tcp_start":[0.5084,-0.01932,0.19314],"tcp_to_object_dist_end":0.02072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02236,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26536,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13666,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.18204,"tcp_end":[0.50039,-0.02238,0.03702],"tcp_start":[0.5086,-0.02257,0.04609],"tcp_to_object_dist_end":0.01734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,-0.02233,0.22242],"object_pos_start":[0.5136,-0.02236,0.02579],"object_to_goal_dist_end":0.18048,"object_to_goal_dist_start":0.26536,"object_z_max":0.22215,"peak_contact_force":0.01017,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28098.0,"raw_peak_contact_force":0.466,"tcp_end":[0.49744,-0.02229,0.23859],"tcp_start":[0.50039,-0.02238,0.03702],"tcp_to_object_dist_end":0.01835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1088.0,"n_steps_budget":1000.0,"object_pos_end":[0.54717,0.12111,0.01602],"object_pos_start":[0.50611,-0.02233,0.22242],"object_to_goal_dist_end":0.20834,"object_to_goal_dist_start":0.18048,"object_z_max":0.33117,"peak_contact_force":9749.08068,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18314.0,"raw_peak_contact_force":2.69845,"subtask_id":"place_goal","tcp_end":[0.55243,0.14701,0.45783],"tcp_start":[0.54956,0.13845,0.44771],"tcp_to_object_dist_end":0.4426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.54717,0.12111,0.01602],"object_pos_start":[0.54717,0.12111,0.01602],"object_to_goal_dist_end":0.20834,"object_to_goal_dist_start":0.20834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4703.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55145,0.15051,0.25852],"tcp_start":[0.55243,0.14701,0.45783],"tcp_to_object_dist_end":0.24432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.54717,0.12111,0.01602],"object_pos_start":[0.54717,0.12111,0.01602],"object_to_goal_dist_end":0.20834,"object_to_goal_dist_start":0.20834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1227.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54719,0.14924,0.2905],"tcp_start":[0.54724,0.14918,0.28032],"tcp_to_object_dist_end":0.27592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.54717,0.12111,0.01602],"object_pos_start":[0.54717,0.12111,0.01602],"object_to_goal_dist_end":0.20834,"object_to_goal_dist_start":0.20834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":912.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55142,0.1507,0.35231],"tcp_start":[0.54719,0.14924,0.2905],"tcp_to_object_dist_end":0.33762,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2963,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.24725,"descend_to_grasp.descend_offset":0.01256,"descend_to_grasp.speed":0.11628,"descend_to_place.place_z_offset":0.00016,"descend_to_place.speed":0.05952,"grasp_object.max_duration":0.63663,"lift_object.lift_height":0.18308,"lift_object.speed":0.03604,"release_object.release_duration":0.4456,"retract_from_place.speed":0.15734,"transport_to_goal.speed":0.24396},"optimized_scores":{"best_composite_score":-0.05022,"best_fitness_score":0.67978,"best_task_score":0.41682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.56208,0.23365,-0.00379],"force_p95":0.9145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45898,"mean_force":0.20957,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5561,0.22606,0.37132]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.49735,0.04297,-0.00159],"force_p95":0.44759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46558,"mean_force":0.19063,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48733,0.04317,0.03953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12152.0,"contact_point_centroid":[0.48446,0.06215,0.11958],"force_p95":0.07441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27702,"mean_force":0.0499,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48489,0.04295,0.11814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10341.0,"contact_point_centroid":[0.51207,0.08921,0.26172],"force_p95":0.10773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24042,"mean_force":0.06878,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50867,0.10808,0.25988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12168.0,"contact_point_centroid":[0.48431,0.02375,0.11953],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23961,"mean_force":0.04903,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48489,0.04295,0.1179]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04485,-0.00215],"force_p95":0.16393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23148,"mean_force":0.13378,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4896,0.04339,0.03982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11456.0,"contact_point_centroid":[0.51297,0.12903,0.2631],"force_p95":0.09883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21322,"mean_force":0.06433,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5095,0.11022,0.26187]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49831,0.0182,0.24709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5035.0,"contact_point_centroid":[0.48835,0.02404,0.04176],"force_p95":0.07096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12514,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48846,0.04328,0.03859]},{"body_a":"world","body_b":"grasp_target","contact_count":2552.0,"contact_point_centroid":[0.56147,0.23368,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12273,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.56074,0.24084,0.26945]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49587,0.04086,0.11906]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.56147,0.23368,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55604,0.24072,0.16164]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.56147,0.23368,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55691,0.24118,0.23118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5526.0,"contact_point_centroid":[0.48817,0.06261,0.04116],"force_p95":0.07059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07417,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48846,0.04328,0.0386]},{"body_a":"left_finger","body_b":"right_finger","contact_count":764.0,"contact_point_centroid":[0.55702,0.22731,0.37464],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01085,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5566,0.22729,0.37247]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2714.0,"contact_point_centroid":[0.56119,0.24089,0.27149],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.56074,0.24085,0.26923]}],"total_contact_groups":17},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56147,0.23368,0.01602],"final_tcp_position":[0.56119,0.2432,0.27734],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":2.45898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49786,0.03794,0.19273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49643,0.044,0.04724],"tcp_start":[0.49786,0.03794,0.19273],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.0437,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24328,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15785,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12361.0,"raw_peak_contact_force":0.23148,"tcp_end":[0.48843,0.04328,0.03856],"tcp_start":[0.49643,0.044,0.04724],"tcp_to_object_dist_end":0.01824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.04312,0.18555],"object_pos_start":[0.50113,0.0437,0.02548],"object_to_goal_dist_end":0.21709,"object_to_goal_dist_start":0.24328,"object_z_max":0.18527,"peak_contact_force":0.07256,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24412.0,"raw_peak_contact_force":0.46558,"tcp_end":[0.4852,0.04297,0.202],"tcp_start":[0.48843,0.04328,0.03856],"tcp_to_object_dist_end":0.01876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1066.0,"n_steps_budget":1000.0,"object_pos_end":[0.5614,0.23387,0.01598],"object_pos_start":[0.49423,0.04312,0.18555],"object_to_goal_dist_end":0.13129,"object_to_goal_dist_start":0.21709,"object_z_max":0.30242,"peak_contact_force":0.12274,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23337.0,"raw_peak_contact_force":2.45898,"subtask_id":"place_goal","tcp_end":[0.56142,0.2394,0.38317],"tcp_start":[0.55895,0.23257,0.37795],"tcp_to_object_dist_end":0.36723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.56147,0.23368,0.01602],"object_pos_start":[0.56148,0.23367,0.01602],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13126,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5266.0,"raw_peak_contact_force":0.12273,"subtask_id":"place_goal","tcp_end":[0.56068,0.24285,0.15574],"tcp_start":[0.56142,0.2394,0.38317],"tcp_to_object_dist_end":0.14002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.56147,0.23368,0.01602],"object_pos_start":[0.56147,0.23368,0.01602],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1225.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55482,0.24019,0.18656],"tcp_start":[0.55481,0.2401,0.1764],"tcp_to_object_dist_end":0.17079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":600.0,"object_pos_end":[0.56147,0.23368,0.01602],"object_pos_start":[0.56147,0.23368,0.01602],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56119,0.2432,0.27734],"tcp_start":[0.55482,0.24019,0.18656],"tcp_to_object_dist_end":0.26149,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69406,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.13055,"descend_to_grasp.descend_offset":0.0116,"descend_to_grasp.speed":0.1484,"descend_to_place.place_z_offset":0.02574,"descend_to_place.speed":0.12189,"grasp_object.max_duration":1.22884,"lift_object.lift_height":0.16707,"lift_object.speed":0.03637,"release_object.release_duration":0.42343,"retract_from_place.speed":0.1985,"transport_to_goal.speed":0.15173},"optimized_scores":{"best_composite_score":-0.10468,"best_fitness_score":0.62532,"best_task_score":0.30608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":322.0,"contact_point_centroid":[0.60798,0.18541,-0.00579],"force_p95":1.31861,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06067,"mean_force":0.31718,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.6195,0.14909,0.2292]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.47217,-0.01963,-0.00148],"force_p95":0.43751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45253,"mean_force":0.20167,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46316,-0.01956,0.03968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2302.0,"contact_point_centroid":[0.59187,0.09746,0.30796],"force_p95":0.17378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33066,"mean_force":0.11405,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.58787,0.11573,0.31192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9936.0,"contact_point_centroid":[0.46096,-0.03863,0.11288],"force_p95":0.07554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25573,"mean_force":0.0526,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46074,-0.01948,0.11102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9930.0,"contact_point_centroid":[0.46094,-0.00033,0.11298],"force_p95":0.07417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25436,"mean_force":0.05243,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46074,-0.01948,0.11106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2789.0,"contact_point_centroid":[0.5937,0.13537,0.30268],"force_p95":0.14998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24949,"mean_force":0.09883,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.58962,0.11761,0.30705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13295.0,"contact_point_centroid":[0.51729,0.01922,0.26404],"force_p95":0.11162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19073,"mean_force":0.07307,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51359,0.03806,0.26273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14620.0,"contact_point_centroid":[0.51632,0.05579,0.26233],"force_p95":0.1049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18711,"mean_force":0.06723,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5126,0.03705,0.2613]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02007,-0.00205],"force_p95":0.13747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17852,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46528,-0.0196,0.03994]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48841,-0.00801,0.24829]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.60885,0.18661,-0.00196],"force_p95":0.13143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13663,"mean_force":0.12294,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61971,0.1525,0.22326]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47324,-0.01824,0.11975]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.60884,0.18661,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.62271,0.15483,0.28343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.46423,-0.00036,0.04125],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09824,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46418,-0.01958,0.03884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46408,-0.03879,0.04078],"force_p95":0.06655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08427,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46418,-0.01958,0.03884]},{"body_a":"left_finger","body_b":"right_finger","contact_count":196.0,"contact_point_centroid":[0.62181,0.15099,0.22673],"force_p95":0.01554,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01184,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.62132,0.15099,0.22459]}],"total_contact_groups":17},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60884,0.18661,0.01602],"final_tcp_position":[0.62819,0.15774,0.32051],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273007.87819,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47701,-0.01683,0.19419],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47191,-0.01975,0.04665],"tcp_start":[0.47701,-0.01683,0.19419],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01968,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1356,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.17852,"tcp_end":[0.46415,-0.01957,0.03881],"tcp_start":[0.47191,-0.01975,0.04665],"tcp_to_object_dist_end":0.01763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.46956,-0.0195,0.1707],"object_pos_start":[0.47607,-0.01968,0.02581],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.28826,"object_z_max":0.17041,"peak_contact_force":0.0739,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19951.0,"raw_peak_contact_force":0.45253,"tcp_end":[0.46089,-0.01947,0.18621],"tcp_start":[0.46415,-0.01957,0.03881],"tcp_to_object_dist_end":0.01777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5817,0.10223,0.31782],"object_pos_start":[0.46956,-0.0195,0.1707],"object_to_goal_dist_end":0.14849,"object_to_goal_dist_start":0.24187,"object_z_max":0.31766,"peak_contact_force":0.15422,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27915.0,"raw_peak_contact_force":0.19073,"subtask_id":"place_goal","tcp_end":[0.57548,0.10185,0.35189],"tcp_start":[0.46089,-0.01947,0.18621],"tcp_to_object_dist_end":0.03464,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.60904,0.18657,0.01699],"object_pos_start":[0.5817,0.10223,0.31782],"object_to_goal_dist_end":0.1766,"object_to_goal_dist_start":0.14849,"object_z_max":0.31786,"peak_contact_force":273007.87819,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5609.0,"raw_peak_contact_force":2.06067,"subtask_id":"place_goal","tcp_end":[0.62367,0.15353,0.21835],"tcp_start":[0.57548,0.10185,0.35189],"tcp_to_object_dist_end":0.20458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.60884,0.18661,0.01602],"object_pos_start":[0.60904,0.18657,0.01699],"object_to_goal_dist_end":0.17758,"object_to_goal_dist_start":0.1766,"object_z_max":0.01699,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1226.0,"raw_peak_contact_force":0.13663,"tcp_end":[0.6187,0.15221,0.24783],"tcp_start":[0.61868,0.15215,0.2376],"tcp_to_object_dist_end":0.23456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":600.0,"object_pos_end":[0.60884,0.18661,0.01602],"object_pos_start":[0.60884,0.18661,0.01602],"object_to_goal_dist_end":0.17758,"object_to_goal_dist_start":0.17758,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62819,0.15774,0.32051],"tcp_start":[0.6187,0.15221,0.24783],"tcp_to_object_dist_end":0.30647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```